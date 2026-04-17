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

    BEHIND_PROXY: bool


defaultconfig = {
    "USERNAME_MIN_CHARS": 4,
    "USERNAME_MAX_CHARS": 24,
    "POST_MAX_CHARS": 300,
    "USER_MAX_POSTS": 15,
    "RATE_LIMIT": 500,
    "RATE_LIMIT_WINDOW": 60,
    "BEHIND_PROXY": False,
}

try:
    # binary mode because that's how tomllib works
    with open("config.toml", "rb") as file:
        fileconfig = tomllib.load(file)
except FileNotFoundError:
    print("No config file found, using defaults...")
    fileconfig = {}

# using cast makes type checking assume that the Any part from the file will still adhere to the type schema
# otherwise ty will give type error and that will be annoying to deal with
# (maybe this isn't the best way to do this and a type check ignore would be better?)
config = cast(ConfigFileTypes, defaultconfig | fileconfig)

# this could be improved, but this lets me not refactor for now
USERNAME_MIN_CHARS = config["USERNAME_MIN_CHARS"]
USERNAME_MAX_CHARS = config["USERNAME_MAX_CHARS"]
POST_MAX_CHARS = config["POST_MAX_CHARS"]
USER_MAX_POSTS = config["USER_MAX_POSTS"]
RATE_LIMIT = config["RATE_LIMIT"]  # requests per time window
RATE_LIMIT_WINDOW = config["RATE_LIMIT_WINDOW"]  # time window for requests
BEHIND_PROXY = config["BEHIND_PROXY"]
