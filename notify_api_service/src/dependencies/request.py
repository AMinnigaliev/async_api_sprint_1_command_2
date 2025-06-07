from fastapi import HTTPException, Request, status


def get_request_id(request: Request) -> str:
    if x_request_id := request.headers.get("X-Request-Id"):
        return x_request_id

    raise HTTPException(
        status_code=status.HTTP_400_BAD_REQUEST,
        detail="X-Request-Id header is required"
    )
