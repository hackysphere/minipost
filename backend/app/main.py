import os
import logging
import logging.handlers
import sys
import uuid

import uvicorn
from fastapi import FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.routing import APIRoute
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

from . import config, db, ratelimit

DEVMODE = "dev" in sys.argv

if not os.path.exists(config.DATA_FOLDER):
    print("data directory does not exist, creating...")
    os.mkdir(config.DATA_FOLDER)

# this only saves my logs, for builtin uvicorn loggers see: https://stackoverflow.com/a/77007723
logger_formatter = logging.Formatter(
    "{asctime} {levelname} - {module}: {message}", style="{"
)
file_logger = logging.handlers.RotatingFileHandler(
    f"{config.DATA_FOLDER}/minipost.log",
    maxBytes=5000000,  # 5MB
    backupCount=5,
)
file_logger.setFormatter(logger_formatter)
console_logger = logging.StreamHandler()
console_logger.setFormatter(logger_formatter)
logger = logging.getLogger("socialapp")
logger.addHandler(file_logger)
logger.addHandler(console_logger)
logger.setLevel(logging.INFO)


database = db.Database()

logger.info("welcome to minipost!")


class NewPostBodyOLD(BaseModel):
    content: str
    user_id: uuid.UUID


def generate_unique_api_id(route: APIRoute):
    # in the case that endpoint duplicates are created, add tags to all routes and uncomment the below line
    # return f"{route.tags[0]}-{route.name}"
    return f"{route.name}"


def validate_post_content(content: str):
    post_content = content.strip()

    if len(post_content) == 0:
        raise ValueError("Empty post content")

    if len(post_content) > config.POST_MAX_CHARS:
        raise ValueError(f"Post cannot be more than {config.POST_MAX_CHARS} characters")

    return post_content


def clean_up_posts(user_id: uuid.UUID):
    if len(userposts := database.get_posts_by_userid(user_id)) > config.USER_MAX_POSTS:
        for post in userposts[config.USER_MAX_POSTS :]:
            database.delete_post(post["uuid"])


if DEVMODE:
    app = FastAPI(generate_unique_id_function=generate_unique_api_id)
    app.add_middleware(
        CORSMiddleware,  # ty:ignore[invalid-argument-type, unused-ignore-comment]
        allow_origins=[
            "http://localhost:5173",
        ],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
else:
    app = FastAPI(
        generate_unique_id_function=generate_unique_api_id,
        docs_url=None,
        redoc_url=None,
        openapi_url=None,
    )
# this applies to ALL ROUTES, including docs and the frontend!!!
if config.RATE_LIMIT != -1:
    app.middleware("http")(ratelimit.rate_limit_by_ip)


@app.get("/api/posts")
def get_latest_posts(count: int = 15) -> list[db.Post]:
    if count > config.MAX_LATEST_POSTS:
        count = config.MAX_LATEST_POSTS
    if count < 1:
        count = 1
    return database.pull_latest_posts(count)


@app.post("/api/posts", status_code=status.HTTP_201_CREATED)
def push_post(body: NewPostBodyOLD) -> db.Post:
    try:
        post_content = validate_post_content(body.content)
    except ValueError as err:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=err.args[0])

    post_userid = body.user_id

    returnval = database.push_post(content=post_content, user_id=post_userid)
    clean_up_posts(post_userid)
    return returnval


@app.get("/api/posts/{post_uuid}")
def get_post_by_uuid(post_uuid: uuid.UUID) -> db.Post:
    try:
        return database.get_post(post_uuid)
    except KeyError as err:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=err.args[0])


@app.delete("/api/posts/{post_uuid}")
def delete_post_by_uuid(post_uuid: uuid.UUID):
    try:
        database.delete_post(post_uuid)
    except KeyError as err:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=err.args[0])


@app.post("/api/posts/{post_uuid}/reply", status_code=status.HTTP_201_CREATED)
def push_reply(post_uuid: uuid.UUID, body: NewPostBodyOLD) -> db.ReplyReturn:
    try:
        post_content = validate_post_content(body.content)
    except ValueError as err:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=err.args[0])

    post_userid = body.user_id

    return database.push_reply(
        content=post_content, user_id=post_userid, reply_to=post_uuid
    )


@app.delete("/api/replies/{reply_uuid}")
def delete_reply_by_uuid(reply_uuid: uuid.UUID):
    try:
        database.delete_reply(reply_uuid)
    except KeyError as err:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=err.args[0])


@app.get("/api/users/{user_id}/posts")
def get_posts_from_userid(user_id: uuid.UUID) -> list[db.Post]:
    try:
        return database.get_posts_by_userid(user_id)
    except KeyError as err:
        logger.info(f"no posts from user {user_id}")
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=err.args[0])


# below are the dynamic routes (for the frontend and api 404s)
# they must be placed last so that they don't override previous routes


@app.get("/api", include_in_schema=False)
@app.get("/api/{path:path}", include_in_schema=False)
def invalid_api_route() -> None:
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND, detail="API route not found"
    )


if not DEVMODE:
    app.mount("/", StaticFiles(directory="../frontend/build/", html=True))
else:

    @app.get("/", include_in_schema=False)
    @app.get("/{path:path}", include_in_schema=False)
    def no_frontend_in_dev() -> None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="FastAPI is running in dev mode, so the hosted frontend has been disabled.",
        )


def main():
    uvicorn.run(app, host="0.0.0.0", port=8000, proxy_headers=config.BEHIND_PROXY)


if __name__ == "__main__":
    # this can be used for debugging
    main()
