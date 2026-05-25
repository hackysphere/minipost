import secrets
import tomllib
from typing import TypedDict, cast


# TODO: make this use default parameters if they are not defined
class ConfigFileTypes(TypedDict):
    USERNAME_MIN_CHARS: int
    USERNAME_MAX_CHARS: int
    POST_MAX_CHARS: int
    USER_MAX_POSTS: int

    RATE_LIMIT: int
    RATE_LIMIT_WINDOW: int
    MAX_LATEST_POSTS: int

    BEHIND_PROXY: bool

    # this currently does nothing and is just for use in code for paths
    DATA_FOLDER: str


defaultconfig = {
    "USERNAME_MIN_CHARS": 4,
    "USERNAME_MAX_CHARS": 24,
    "POST_MAX_CHARS": 300,
    "USER_MAX_POSTS": 15,
    "RATE_LIMIT": 500,
    "RATE_LIMIT_WINDOW": 60,
    "MAX_LATEST_POSTS": 30,
    "BEHIND_PROXY": False,
    "DATA_FOLDER": "./data",
}

try:
    # binary mode because that's how tomllib works
    with open("./data/config.toml", "rb") as file:
        _fileconfig = tomllib.load(file)
except FileNotFoundError:
    print("No config file found, using defaults...")
    _fileconfig = {}

try:
    with open("./data/jwtkey", "r") as file:
        _jwt_file = list(filter(None, file.readlines()))
    if len(_jwt_file) > 1:
        raise SyntaxError("jwtkey file has multiple lines for the key, please only use one")  # fmt: off

    jwt_key = str(_jwt_file[0]).strip()
    if len(jwt_key) < 32:
        raise ValueError("jwtkey file has less than 32 bytes, which makes the key insecure, please regenerate it")  # fmt: off
except FileNotFoundError:
    print("No JWT key found, creating one...")
    jwt_key = secrets.token_hex(32)

    try:
        with open("./data/jwtkey", "w") as file:
            file.write(jwt_key)
    except FileNotFoundError:
        print("Failed to create jwtkey file, all users will have to reauthenticate on next restart")  # fmt: off


# using cast makes type checking assume that the Any part from the file will still adhere to the type schema
# otherwise ty will give type error and that will be annoying to deal with
# (maybe this isn't the best way to do this and a type check ignore would be better?)
config = cast(ConfigFileTypes, defaultconfig | _fileconfig)

# this could be improved, but this lets me not refactor for now
USERNAME_MIN_CHARS = config["USERNAME_MIN_CHARS"]
USERNAME_MAX_CHARS = config["USERNAME_MAX_CHARS"]
POST_MAX_CHARS = config["POST_MAX_CHARS"]
USER_MAX_POSTS = config["USER_MAX_POSTS"]
RATE_LIMIT = config["RATE_LIMIT"]  # requests per time window
RATE_LIMIT_WINDOW = config["RATE_LIMIT_WINDOW"]  # time window for requests
MAX_LATEST_POSTS = config["MAX_LATEST_POSTS"]
BEHIND_PROXY = config["BEHIND_PROXY"]
DATA_FOLDER = config["DATA_FOLDER"]

JWT_KEY = jwt_key
