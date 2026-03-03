from __future__ import annotations

import logging
from fastapi import APIRouter, Request, Form, Depends, status, HTTPException
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session
from urllib.parse import unquote

from ._templates import templates
from ._render import render
from ._flash import redirect_with_flash, add_flash, FLASH_SUCCESS, FLASH_ERROR, FLASH_INFO
from ._csrf import ensure_csrf_token, validate_csrf
from ...database import get_db
from ... import crud, security, schemas, settings

router = APIRouter(prefix="", tags=["ui"])

COOKIE_NAME = "access_token"
logger = logging.getLogger(__name__)

@router.get("/login")
def login_page(request: Request):
    token = request.cookies.get(COOKIE_NAME)
    if token:
        return RedirectResponse(url="/logs", status_code=303)
    return render(
        request=request,
        name="login.html",
        context={"error": None, "user": None}
    )
    

@router.post("/login")
def login_action(
    request: Request,
    login_id: str = Form(...),
    password: str = Form(...),
    db: Session = Depends(get_db),
    csrf_token: str = Form(...)
):
    """ 
    1. login_id と passwordを受け取る
    2. DBでユーザー確認 and パスワード検証
    3. JWT発行
    4. Cookie保存して /ui/logs にリダイレクト
    """
    validate_csrf(request, csrf_token)
    
    # DBでユーザー確認 and パスワード検証
    user = security.authenticate_user(db=db, login_id=login_id, password=password)
    if not user:
        return render(
            request=request,
            name="login.html",
            context={"request": request, "error": "login_id または password が違います"},
            status_code=400,
        )
    
    # JWT発行
    token = security.create_access_token(data = {"sub": str(user.user_id)})
    
    response = RedirectResponse(url="/logs", status_code=303)
    response.set_cookie(
        key=COOKIE_NAME,
        value=token,
        httponly=True,
        samesite="lax",
        secure=settings.SECURE_COOKIE,
        max_age=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        path="/"
    )
    # return response
    return add_flash(response=response, message="ログインしました", level=FLASH_SUCCESS)

@router.get("/logout")
def logout_action():
    response = RedirectResponse(url="/login", status_code=303)
    response.delete_cookie(COOKIE_NAME, path="/")
    return add_flash(response=response, message="ログアウトしました", level=FLASH_INFO)

@router.get("/register")
def register_page(request: Request):
    return render(
        request=request,
        name="register.html",
        context={"error": None, "user": None}
    )

@router.post("/register")
def register_action(
    request: Request,
    login_id: str = Form(...), # login_idはフォームから送られてくる**必須**項目
    display_name: str = Form(""), # display_nameはフォームから送られてくる**必須ではない**項目
    password: str = Form(...),
    password_confirm: str = Form(...),
    csrf_token: str = Form(...),
    db: Session = Depends(get_db)
):
    validate_csrf(request, csrf_token)
    if password != password_confirm:
        return render(
        request=request,
        name="register.html",
        context={"error": "パスワードが一致しません", "user": None},
        status_code=400,
    )
    if len(password) < 8:
        return render(
        request=request,
        name="register.html",
        context={"error": "パスワードは8文字以上にしてください", "user": None},
        status_code=400,
    )
    try:
        user_in = schemas.UserCreate(login_id=login_id, display_name=display_name, password=password)
        crud.create_user(db=db, user=user_in)
    
    # 想定内エラー
    except HTTPException as e:
        return render(
        request=request,
        name="register.html",
        context={"error": e.detail, "user": None},
        status_code=e.status_code,
    )
        
    # 想定外エラー
    except Exception:
        logger.exception("Unexpected error in register_action")
        return render(
        request=request,
        name="register.html",
        context={"error": "エラーが発生しました。もう一度お試しください", "user": None},
        status_code=500,
    )
        
    return RedirectResponse(url="/login", status_code=303)