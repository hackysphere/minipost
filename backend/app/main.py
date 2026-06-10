import logging
import logging.handlers
import os
import sys
import uuid
from datetime import datetime, timedelta, timezone
from typing import Annotated, Literal

import argon2
import jwt
import uvicorn
from fastapi import Depends, FastAPI, Form, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.routing import APIRoute
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestFormStrict
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
logger = logging.getLogger(__name__)
logger.addHandler(file_logger)
logger.addHandler(console_logger)
logger.setLevel(logging.INFO)


database = db.Database()

logger.info("welcome to minipost!")


class TokenEndpointReturn(BaseModel):
    access_token: str
    token_type: Literal["bearer"]


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


# ====
# auth
# ====


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/token")
hasher = argon2.PasswordHasher()
DUMMY_HASH = hasher.hash(str(uuid.uuid4()))


@app.post("/api/token")
def login(
    form_data: Annotated[OAuth2PasswordRequestFormStrict, Depends()],
) -> TokenEndpointReturn:
    unauthenticated_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid username or password",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        user = database.get_user_by_username(form_data.username)
    except KeyError:
        # hashing a dummy token here in order to make the http401 delay the same even if there is no password to check
        try:
            hasher.verify(DUMMY_HASH, "")
        except argon2.exceptions.Argon2Error:
            pass

        raise unauthenticated_exception
    authdata = database.get_auth_data(user["user_id"])

    try:
        hasher.verify(authdata["pass_hash"], form_data.password)
    except argon2.exceptions.Argon2Error, argon2.exceptions.InvalidHashError:
        raise unauthenticated_exception

    jwt_token = jwt.encode(
        {
            "sub": str(user["user_id"]),
            "exp": datetime.now(timezone.utc) + timedelta(days=config.JWT_EXPIRY),
            "pass_ver": authdata["pass_version"],  # not part of jwt spec
        },
        config.JWT_KEY,
        "HS256",
    )
    return TokenEndpointReturn(access_token=jwt_token, token_type="bearer")


def transform_user_token(token: Annotated[str, Depends(oauth2_scheme)]) -> db.User:
    unauthenticated_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid token",
        headers={"WWW-Authenticate": "Bearer"},
    )

    expired_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Expired token; reauthenticate",
        headers={"WWW-Authenticate": "Bearer"},
    )

    unauthorized_exception = HTTPException(
        status_code=status.HTTP_403_FORBIDDEN, detail="Access forbidden"
    )

    try:
        json_token = jwt.decode(token, config.JWT_KEY, "HS256")
        user_uuid = uuid.UUID(json_token["sub"])
        authdata = database.get_auth_data(user_uuid)

        if datetime.now(timezone.utc).timestamp() > json_token["exp"]:
            raise expired_exception
        if authdata["pass_version"] != json_token["pass_ver"]:
            raise expired_exception
        if authdata["active"] != 1:
            raise unauthorized_exception
    except jwt.ExpiredSignatureError:
        raise expired_exception
    except KeyError, jwt.InvalidTokenError, ValueError:  # ValueError from uuid encoding
        raise unauthenticated_exception

    return database.get_user(user_uuid)


# ===================
# global post getters
# ===================


@app.get("/api/posts")
def get_latest_posts(count: int = 15) -> list[db.Post]:
    if count > config.MAX_LATEST_POSTS:
        count = config.MAX_LATEST_POSTS
    if count < 1:
        count = 1
    return database.get_latest_posts(count)


@app.get("/api/users/{user_id}/posts")
def get_posts_by_userid(user_id: uuid.UUID) -> list[db.Post]:
    try:
        return database.get_posts_by_userid(user_id)
    except KeyError as err:
        logger.info(f"no posts from user {user_id}")
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=err.args[0])


# ===============
# post operations
# ===============


@app.get("/api/posts/{post_uuid}")
def get_post(post_uuid: uuid.UUID) -> db.Post:
    try:
        return database.get_post(post_uuid)
    except KeyError as err:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=err.args[0])


@app.post("/api/posts", status_code=status.HTTP_201_CREATED)
def create_post(
    user: Annotated[db.User, Depends(transform_user_token)],
    body: Annotated[str, Form()],
) -> db.Post:
    try:
        post_content = validate_post_content(body)
    except ValueError as err:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=err.args[0])

    post_userid = user["user_id"]

    returnval = database.create_post(content=post_content, user_id=post_userid)
    clean_up_posts(post_userid)
    return returnval


@app.delete("/api/posts/{post_uuid}")
def delete_post(user: Annotated[db.User, Depends(transform_user_token)], post_uuid: uuid.UUID):  # fmt: off
    try:
        post = database.get_post(post_uuid)
        if post["author"]["user_id"] != user["user_id"]:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Unauthorized to delete post",
            )
        database.delete_post(post_uuid)
    except KeyError as err:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=err.args[0])


# ================
# reply operations
# ================


@app.post("/api/posts/{post_uuid}/reply", status_code=status.HTTP_201_CREATED)
def create_reply(
    user: Annotated[db.User, Depends(transform_user_token)],
    post_uuid: uuid.UUID,
    body: Annotated[str, Form()],
) -> db.Reply:
    try:
        post_content = validate_post_content(body)
    except ValueError as err:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=err.args[0])

    return database.create_reply(
        content=post_content, user_id=user["user_id"], reply_to=post_uuid
    )


@app.delete("/api/replies/{reply_uuid}")
def delete_reply(user: Annotated[db.User, Depends(transform_user_token)], reply_uuid: uuid.UUID):  # fmt: off
    try:
        reply = database.get_reply(reply_uuid)
        if reply["author"]["user_id"] != user["user_id"]:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Unauthorized to delete reply",
            )
        database.delete_reply(reply_uuid)
    except KeyError as err:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=err.args[0])


# ===============
# user operations
# ===============


@app.get("/api/users/{user_id}")
def get_user(user_id: uuid.UUID) -> db.User:
    try:
        return database.get_user(user_id)
    except KeyError as err:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=err.args[0])


# ==================
# account operations
# ==================


@app.get("/api/account/self")
def get_self(user: Annotated[db.User, Depends(transform_user_token)]) -> db.User:
    return user


@app.post("/api/account/changeusername")
def set_username(
    user: Annotated[db.User, Depends(transform_user_token)],
    new_username: Annotated[str, Form()],
):
    try:
        if config.USERNAME_MIN_CHARS <= len(new_username) <= config.USERNAME_MAX_CHARS:
            database.set_user_username(user["user_id"], new_username)
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Username must be between {config.USERNAME_MIN_CHARS} and {config.USERNAME_MAX_CHARS} characters.",
            )
    except ValueError as err:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=err.args[0])


@app.post("/api/account/changepassword")
def set_password(
    user: Annotated[db.User, Depends(transform_user_token)],
    old_password: Annotated[str, Form()],
    new_password: Annotated[str, Form()],
):
    try:
        authdata = database.get_auth_data(user["user_id"])
        hasher.verify(authdata["pass_hash"], old_password)
        database.set_user_password(user["user_id"], hasher.hash(new_password))
        return "Password change, please reauthenticate"
    except argon2.exceptions.VerifyMismatchError:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Invalid password"
        )


@app.post("/api/account/createaccount")
def create_account(
    username: Annotated[str, Form()], password: Annotated[str, Form()]
) -> TokenEndpointReturn:
    try:
        database.create_user(username, hasher.hash(password))
    except ValueError as err:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=err.args[0])
    return login(
        OAuth2PasswordRequestFormStrict(
            grant_type="password", username=username, password=password
        )
    )


@app.delete("/api/account/deleteaccount")
def delete_account(
    user: Annotated[db.User, Depends(transform_user_token)],
    password: Annotated[str, Form()],
):
    try:
        authdata = database.get_auth_data(user["user_id"])
        hasher.verify(authdata["pass_hash"], password)
        database.delete_user(user["user_id"])
        return "Account deleted"
    except argon2.exceptions.VerifyMismatchError:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Invalid password"
        )


# ============
# extra routes
# ============
# below are the extra routes for the frontend and api 404s
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
