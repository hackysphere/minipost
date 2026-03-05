from typing import Annotated
import uvicorn
import uuid
import db
from fastapi import FastAPI, status, HTTPException, Body

app = FastAPI()
database = db.Database()

# do not use async functions, as sqlite3 in python doesn't support async


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
        raise HTTPException(404, err.args[0])


if __name__ == "__main__":
    # this can be used for debugging
    uvicorn.run(app, host="0.0.0.0", port=8000)
