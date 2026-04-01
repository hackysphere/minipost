from pydantic import BaseModel
import uvicorn
import uuid
import sys
import logging
import logging.handlers
from fastapi import FastAPI, status, HTTPException
from fastapi.routing import APIRoute
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from . import db

DEVMODE = "dev" in sys.argv

# this only saves my logs, for builtin uvicorn loggers see: https://stackoverflow.com/a/77007723
logger_formatter = logging.Formatter(
    "{asctime} {levelname} - {module}: {message}", style="{"
)
file_logger = logging.handlers.RotatingFileHandler(
    "minipost.log",
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


def generate_unique_api_id(route: APIRoute):
    # in the case that endpoint duplicates are created, add tags to all routes and uncomment the below line
    # return f"{route.tags[0]}-{route.name}"
    return f"{route.name}"


if DEVMODE:
    app = FastAPI(generate_unique_id_function=generate_unique_api_id)
    app.add_middleware(
        CORSMiddleware,  # ty:ignore[invalid-argument-type]
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


class NewPostBody(BaseModel):
    content: str
    username: str = "null"


@app.get("/api/posts")
def get_latest_posts(count: int = 15) -> list[db.Post]:
    return database.pull_latest_posts(count)


@app.post("/api/posts", status_code=status.HTTP_201_CREATED)
def push_post(body: NewPostBody) -> db.Post:
    if len(body.content.strip()) == 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Empty post content"
        )

    if len(body.username.strip()) == 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="No username provided"
        )

    return database.push_post(content=body.content, user=body.username)


@app.get("/api/posts/{post_uuid}")
def get_post_by_uuid(post_uuid: uuid.UUID) -> db.Post:
    try:
        return database.get_post(post_uuid)
    except KeyError as err:
        logger.info(f"failed to get post {post_uuid}")
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=err.args[0])


@app.get("/api/users/{username}/posts")
def get_posts_from_user(username: str) -> list[db.Post]:
    try:
        return database.get_user_posts(username)
    except KeyError as err:
        logger.info(f"no posts from user {username}")
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=err.args[0])


# below are the dynamic routes (for the frontend and special api 404s)
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


def run_uvicorn():
    uvicorn.run(app, host="0.0.0.0", port=8000)


if __name__ == "__main__":
    # this can be used for debugging
    run_uvicorn()
