from __future__ import annotations

import secrets 
from fastapi import HTTPException, status
from fastapi.responses import Response
from starlette.requests import Request

from ... import settings

CSRF_COOKIE_NAME = "csrf_token"

def ensure_csrf_token(request: Request, response: Response) -> str:
    """ 
    CSRFトークンをcookieから取得、なければ生成してcookieにセット
    """
    token = request.cookies.get(CSRF_COOKIE_NAME)
    if not token:
        token = secrets.token_urlsafe(32)
        response.set_cookie(
            key=CSRF_COOKIE_NAME,
            value=token,
            max_age=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
            httponly=True,
            samesite="lax",
            secure=settings.SECURE_COOKIE,
            path="/"
        )
    return token

def validate_csrf(request: Request, csrf_token_form: str) -> None:
    """ 
    フォームのcsrf_tokenとcookieのcsrf_tokenが一致するか検証
    """
    csrf_token_cookie = request.cookies.get(CSRF_COOKIE_NAME)
    if not csrf_token_cookie or not csrf_token_form:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="CSRF validation failed")
    if csrf_token_cookie != csrf_token_form:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="CSRF validation failed")