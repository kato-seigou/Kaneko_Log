from __future__ import annotations

import logging 
from typing import Optional
from fastapi import APIRouter, Request, Depends, Form, HTTPException
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session
from datetime import date

from ... database import get_db
from ... import crud, models, schemas
from ._templates import templates
from ._deps import require_admin_from_cookie, get_current_user_from_cookie_optional
from ._flash import redirect_with_flash, add_flash, FLASH_SUCCESS, FLASH_ERROR, FLASH_INFO
from ._render import render
from ._csrf import validate_csrf

router = APIRouter(prefix="/discographies", tags=["ui"])

logger = logging.getLogger(__name__)

# ディスコグラフィ一覧表示
@router.get("")
def discographies_page(
    request: Request,
    db: Session = Depends(get_db),
    user: models.User | None = Depends(get_current_user_from_cookie_optional)
):
    if user is None:
        resp = RedirectResponse(url="/login", status_code=303)
        return add_flash(resp, "ログインしてください", level=FLASH_INFO)
    
    discographies = crud.get_discographies(db=db)
    # return templates.TemplateResponse(
    #     "discographies.html",
    #     {"request": request, "discographies": discographies, "user": user}
    # )
    return render(
        request=request,
        name="discographies.html",
        context={"discographies": discographies, "user": user}
    )
    
# 登録画面（管理者のみ）
@router.get("/new")
def new_discography_page(
    request: Request,
    admin_user: models.User = Depends(require_admin_from_cookie)
):
    # return templates.TemplateResponse(
    #     "discography_new.html",
    #     {"request": request, "user": admin_user, "error": None}
    # )
    return render(
        request=request,
        name="discography_new.html",
        context={"user": admin_user, "error": None}
    )

# 登録処理（管理者のみ）
@router.post("/new")
def create_discographies_action(
    request: Request,
    discography_title: str = Form(...),
    discography_num: int | None = Form(None),
    discography_type: str = Form(...),
    released_date: date = Form(...),
    playtime_seconds: str | None = Form(None),
    discography_link: str | None = Form(None),
    db: Session = Depends(get_db),
    admin_user: models.User = Depends(require_admin_from_cookie),
    csrf_token: str = Form(...)
):
    validate_csrf(request, csrf_token)
    try:
        discography_in = schemas.DiscographyCreate(
            discography_title=discography_title,
            discography_num=int(discography_num) if discography_num else None,
            discography_type=discography_type,
            released_date=released_date,
            playtime_seconds=int(playtime_seconds) if playtime_seconds else None,
            discography_link=discography_link if discography_link else None,
        )
        crud.create_discography(db=db, discography=discography_in)
    except Exception as e:
        return templates.TemplateResponse(
            "discography_new.html", 
            {"request": request, "user": admin_user, "error": str(e)}
        )
        
    return RedirectResponse(
        url="/discographies", status_code=303
    )
    
# 編集（管理者のみ）
@router.get("/{discography_id}/edit")
def edit_discography_page(
    discography_id: int,
    request: Request,
    db: Session = Depends(get_db),
    admin_user: models.User = Depends(require_admin_from_cookie)
):  

    discography = crud.get_discography(db=db, discography_id=discography_id)
    if discography is None:
        # return templates.TemplateResponse(
        #     "discography_edit.html",
        #     {
        #         "request": request,
        #         "discography": None,
        #         "user": admin_user,
        #         "error": "対象のディスコグラフィが存在しません"
        #     }
        # )
        return render(
        request=request,
        name="discography_edit.html",
        context={"discography": None, "user": admin_user, "error": "対象のディスコグラフィが存在しません"},
        status_code=404,
    )
    # return templates.TemplateResponse(
    #     "discography_edit.html",
    #     {"request": request, "discography": discography, "user": admin_user, "error": None}
    # )
    return render(
    request=request,
    name="discography_edit.html",
    context={"discography": discography, "user": admin_user, "error": None},
    )
    
@router.post("/{discography_id}/edit")
def edit_discography_action(
    request: Request,
    discography_id: int, 
    db: Session = Depends(get_db),
    discography_title: str = Form(...),
    discography_type: str = Form(...),
    released_date: date = Form(...),
    discography_num: Optional[int] = Form(None),
    playtime_seconds: Optional[int] = Form(None),  
    discography_link: Optional[str] = Form(None), 
    admin_user: models.User = Depends(require_admin_from_cookie),
    csrf_token: str = Form(...)
):
    validate_csrf(request, csrf_token)
    
    discography_link = (discography_link or "").strip()
    discography_link = None if discography_link in ("", "None") else discography_link

        
    try: 
        crud.update_discography(
            db=db, 
            discography_id=discography_id,
            disco_update=schemas.DiscographyUpdate(
                discography_title=discography_title,
                discography_type=discography_type,
                released_date=released_date,
                discography_num=discography_num,
                playtime_seconds=playtime_seconds,
                discography_link=discography_link
            )
        )
        return RedirectResponse(url="/discographies", status_code=303)
    except Exception as e:
        discography = crud.get_discography(db=db, discography_id=discography_id)
        return templates.TemplateResponse(
            "discography_edit.html",
            {
                "request": request,
                "discography": discography,
                "user": admin_user,
                "error": str(e)
            }
        )
        
@router.post("/{discography_id}/delete")
def delete_discography_action(
    request: Request,
    discography_id: int,
    db: Session = Depends(get_db),
    admin_user: models.User = Depends(require_admin_from_cookie),
    csrf_token: str = Form(...)
):
    validate_csrf(request, csrf_token)
    try:
        crud.delete_discography(db=db, discography_id=discography_id)
        return RedirectResponse(url="/discographies", status_code=303)
    except Exception as e:
        discography = crud.get_discography(db=db, discography_id=discography_id)
        return templates.TemplateResponse(
            "discography_edit.html",
            {
                "request": request,
                "discography": discography,
                "user": admin_user,
                "error": e.detail
            },
            status_code=e.status_code
        )
    
    except Exception:
        logger.exception("Unexpected error in delete_discography_action")
        return templates.TemplateResponse(
            "discography_edit.html",
            {
                "request": request,
                "discography": discography,
                "user": admin_user,
                "error": "エラーが発生しました。もう一度お試しください。"
            }
        )