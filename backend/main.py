from typing import Annotated
import uvicorn
import uuid
import db
import sys
import logging
import logging.handlers
from fastapi import FastAPI, status, HTTPException, Body
from fastapi.routing import APIRoute
from fastapi.middleware.cors import CORSMiddleware


# this only saves my logs, for builtin uvicorn loggers see: https://stackoverflow.com/a/77007723
file_logger = logging.handlers.RotatingFileHandler(
    "app.log",
    maxBytes=5000000,  # 5MB
    backupCount=5,
)
file_logger.setFormatter(
    logging.Formatter("{asctime} {levelname} - {module}: {message}", style="{")
)
# this is prefixed with uvicorn so that it shows up automatically in the console
logger = logging.getLogger("uvicorn.socialapp")
logger.addHandler(file_logger)
logger.setLevel(logging.INFO)

logger.info("starting up app")

database = db.Database()


def generate_unique_api_id(route: APIRoute):
    # in the case that endpoint duplicates are created, add tags to all routes and uncomment the below line
    # return f"{route.tags[0]}-{route.name}"
    return f"{route.name}"


app = FastAPI(generate_unique_id_function=generate_unique_api_id)
if "dev" in sys.argv:
    app.add_middleware(
        CORSMiddleware,  # ty:ignore[invalid-argument-type]
        allow_origins=[
            "http://localhost:5173",
        ],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )


@app.get("/api/posts/latest")
def get_latest_posts(count: int = 15) -> list[db.Post]:
    return database.pull_latest_posts(count)


@app.post("/api/posts/publish", status_code=status.HTTP_201_CREATED)
def push_post(body: Annotated[str, Body(media_type="text/plain")]) -> db.Post:
    return database.push_post(body)


@app.get("/api/posts/uuid/{post_uuid}")
def get_post_by_uuid(post_uuid: uuid.UUID) -> db.Post:
    try:
        return database.get_post(post_uuid)
    except KeyError as err:
        logger.info(f"failed to get post {post_uuid}")
        raise HTTPException(404, err.args[0])


if __name__ == "__main__":
    # this can be used for debugging
    uvicorn.run(app, host="0.0.0.0", port=8000)
