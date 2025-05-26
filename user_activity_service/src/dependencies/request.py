from fastapi import Request


def get_request_id(request: Request) -> str:
    return request.headers.get("X-Request-Id")
