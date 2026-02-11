from __future__ import annotations

from fastapi import APIRouter, Request, Form, Depends, status
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session
from urllib.parse import unquote

from ._templates import templates
from ._render import render
from ._flash import redirect_with_flash, add_flash, FLASH_SUCCESS, FLASH_ERROR, FLASH_INFO
from ...database import get_db
from ... import crud, security, schemas

router = APIRouter(prefix="/ui", tags=["ui"])

COOKIE_NAME = "access_token"

@router.get("/login")
def login_page(request: Request):
    token = request.cookies.get(COOKIE_NAME)
    if token:
        return RedirectResponse(url="/ui/logs", status_code=303)
    # return templates.TemplateResponse(
    #     "login.html", {"request": request, "error": None, "user": None}
    # )
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
    db: Session = Depends(get_db)
):
    """ 
    1. login_id と passwordを受け取る
    2. DBでユーザー確認 and パスワード検証
    3. JWT発行
    4. Cookie保存して /ui/logs にリダイレクト
    """
    
    # DBでユーザー確認 and パスワード検証
    user = security.authenticate_user(db=db, login_id=login_id, password=password)
    if not user:
        # return templates.TemplateResponse(
        #     "login.html",
        #     {"request": request, "error": "login_id または password が違います"},
        #     status_code=400,
        # )
        return render(
            request=request,
            name="login.html",
            context={"request": request, "error": "login_id または password が違います"},
            status_code=400,
        )
    
    # JWT発行
    token = security.create_access_token(data = {"sub": str(user.user_id)})
    
    response = RedirectResponse(url="/ui/logs", status_code=303)
    response.set_cookie(
        key=COOKIE_NAME,
        value=token,
        httponly=True,
        samesite="lax",
        secure=False,
        max_age=60 * 60,
        path="/"
    )
    # return response
    return add_flash(response=response, message="ログインしました", level=FLASH_SUCCESS)

@router.get("/logout")
def logout_action():
    response = RedirectResponse(url="/ui/login", status_code=303)
    response.delete_cookie(COOKIE_NAME, path="/")
    return add_flash(response=response, message="ログアウトしました", level=FLASH_INFO)

@router.get("/register")
def register_page(request: Request):
    # return templates.TemplateResponse(
    #     "register.html", {"request": request, "error": None, "user": None}
    #     )
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
    db: Session = Depends(get_db)
):
    if password != password_confirm:
        return templates.TemplateResponse(
            "register.html",
            {"request": request, "error": "パスワードが一致しません"},
            status_code=303
        )
    if len(password) < 8:
        return templates.TemplateResponse(
            "register.html",
            {"request": request, "error": "パスワードは8文字以上にしてください"},
            status_code=400
        )
    try:
        user_in = schemas.UserCreate(login_id=login_id, display_name=display_name, password=password)
        crud.create_user(db=db, user=user_in)
    except Exception as e:
        return templates.TemplateResponse(
            "register.html",
            {"request": request, "error": str(e)},
            status_code=400
        )
    return RedirectResponse(url="/ui/login", status_code=303)