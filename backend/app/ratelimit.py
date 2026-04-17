import time
from typing import TypedDict
from fastapi import Request, status
from fastapi.responses import PlainTextResponse
from . import config


class IPRateData(TypedDict):
    initial_timestamp: float
    request_count: int


ip_list: dict[str, IPRateData] = {}


# most of this is taken from https://stackoverflow.com/questions/65491184/ratelimit-in-fastapi
async def rate_limit_by_ip(request: Request, call_next):
    # the following is to make ty happy because the client can be None type
    # using a string instead of None because None cannot be accessed as a key, and rate limiting should fail closed
    client_ip = "null"
    if request.client:
        client_ip = request.client.host

    if client_ip not in ip_list:
        ip_list[client_ip] = IPRateData(initial_timestamp=time.time(), request_count=1)
    else:
        # could probably put this if statement into the one above and join with OR
        if time.time() >= (
            ip_list[client_ip]["initial_timestamp"] + config.RATE_LIMIT_WINDOW
        ):
            ip_list[client_ip] = IPRateData(
                initial_timestamp=time.time(), request_count=1
            )
        else:
            ip_list[client_ip]["request_count"] += 1

            if ip_list[client_ip]["request_count"] > config.RATE_LIMIT:
                return PlainTextResponse(
                    "Rate limit exceeded, please wait a bit",
                    status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                )

    return await call_next(request)
