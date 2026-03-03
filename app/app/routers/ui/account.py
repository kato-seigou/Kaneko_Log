from __future__ import annotations

import logging 
from typing import Optional
from fastapi import APIRouter, Request, Depends, Form, HTTPException
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session
from datetime import date

from ... database import get_db
from ... import crud, models, schemas, security
from ._templates import templates
from ._deps import require_admin_from_cookie, get_current_user_from_cookie_optional
from ._flash import redirect_with_flash, add_flash, FLASH_SUCCESS, FLASH_ERROR, FLASH_INFO
from ._render import render
from ._csrf import validate_csrf
from .auth import COOKIE_NAME

router = APIRouter(prefix="/account", tags=["ui"])

logger = logging.getLogger(__name__)

# ユーザー取得はget_current_user_from_cookieで可

# アカウント編集ページ表示
@router.get("/edit")
def account_edit_page(
    request: Request,
    current_user: models.User | None = Depends(get_current_user_from_cookie_optional)
):
    if current_user is None:
        return RedirectResponse(url="/ui/login", status_code=303)
        
    return render(
        request=request,
        name="account_edit.html",
        context={"user": current_user, "error": None}
    )

# プロフィール更新アクション
@router.post("/profile")
def account_profile_update_action(
    request: Request,
    db: Session = Depends(get_db),
    login_id: str = Form(...),
    display_name: str = Form(""),
    csrf_token: str = Form(...),
    current_user: models.User | None = Depends(get_current_user_from_cookie_optional)
):
    if current_user is None:
        return RedirectResponse(url="/ui/login", status_code=303)
    
    validate_csrf(request, csrf_token)
    
    try:
        crud.update_user_profile(
            db=db,
            user_id=current_user.user_id,
            upd=schemas.UserProfileUpdate(
                login_id=login_id,
                display_name=display_name
            )
        )
    except HTTPException as e:
        return render(
            request=request,
            name="account_edit.html",
            context={"user": current_user, "error": e.detail},
            status_code=e.status_code,
        )
    
    except Exception:
        logger.exception("Unexpected error in account_profile_update_action")
        return render(
            request=request,
            name="account_edit.html",
            context={"user": current_user, "error": "エラーが発生しました。もう一度お試しください"},
            status_code=500,
        )
        
    return redirect_with_flash(
        url="/account/edit",
        message="プロフィールを更新しました",
        level=FLASH_SUCCESS
    )
    
# パスワード更新
@router.post("/password")
def account_password_update_action(
    request: Request,
    db: Session = Depends(get_db),
    current_password: str = Form(...),
    new_password: str =  Form(...),
    new_password_confirm: str = Form(...),
    csrf_token: str = Form(...),
    current_user: models.User | None = Depends(get_current_user_from_cookie_optional)
):
    if current_user is None:
        return RedirectResponse(url="/ui/login", status_code=303)
    
    validate_csrf(request, csrf_token)
    
    # new_password == confirm
    if new_password != new_password_confirm:
        return render(
            request=request,
            name="account_edit.html",
            context={"user": current_user, "error": "パスワードが一致しません"},
            status_code=400
        )
        
    if len(new_password) < 8:
        return render(
            request=request,
            name="account_edit.html",
            context={"user": current_user, "error": "パスワードは8文字以上にしてください"},
            status_code=400
        )
        
    try: 
        crud.update_user_password(
            db=db,
            user_id=current_user.user_id,
            upd=schemas.UserPasswordUpdate(
                current_password=current_password,
                new_password=new_password
            )
        )
    except HTTPException as e:
        return render(
            request=request,
            name="account_edit.html",
            context={"user": current_user, "error": e.detail},
            status_code=e.status_code,
        )
    except Exception:
        logger.exception("Unexpected error in account_password_update_action")
        return render(
            request=request,
            name="account_edit.html",
            context={"user": current_user, "error": "エラーが発生しました。もう一度お試しください"},
            status_code=500,
        )
    
    response = RedirectResponse(url="/ui/login", status_code=303)
    response.delete_cookie(COOKIE_NAME, path="/")
    return add_flash(
        response=response,
        message="パスワードを更新しました。再度ログインしてください",
        level=FLASH_SUCCESS
    )