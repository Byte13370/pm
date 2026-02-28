from fastapi import HTTPException, Request


AUTH_COOKIE_NAME = "pm_auth"
AUTH_COOKIE_VALUE = "1"
AUTH_USERNAME = "user"


def require_authenticated_username(request: Request) -> str:
    if request.cookies.get(AUTH_COOKIE_NAME) == AUTH_COOKIE_VALUE:
        return AUTH_USERNAME

    raise HTTPException(status_code=401, detail="Authentication required")
