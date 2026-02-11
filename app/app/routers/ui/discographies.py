from __future__ import annotations

from typing import Optional
from fastapi import APIRouter, Request, Depends, Form
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session
from datetime import date

from ... database import get_db
from ... import crud, models, schemas
from ._templates import templates
from ._deps import require_admin_from_cookie, get_current_user_from_cookie_optional
from ._flash import add_flash, FLASH_INFO

router = APIRouter(prefix="/ui", tags=["ui"])



# ディスコグラフィ一覧表示
@router.get("/discographies")
def discographies_page(
    request: Request,
    db: Session = Depends(get_db),
    user: models.User | None = Depends(get_current_user_from_cookie_optional)
):
    if user is None:
        resp = RedirectResponse(url="/ui/login", status_code=303)
        return add_flash(resp, "ログインしてください", level=FLASH_INFO)
    
    discographies = crud.get_discographies(db=db)
    return templates.TemplateResponse(
        "discographies.html",
        {"request": request, "discographies": discographies, "user": user}
    )
    
# 登録画面（管理者のみ）
@router.get("/discographies/new")
def new_discography_page(
    request: Request,
    admin_user: models.User = Depends(require_admin_from_cookie)
):
    return templates.TemplateResponse(
        "discography_new.html",
        {"request": request, "user": admin_user, "error": None}
    )

# 登録処理（管理者のみ）
@router.post("/discographies/new")
def create_discographies_action(
    request: Request,
    discography_title: str = Form(...),
    discography_num: int | None = Form(None),
    discography_type: str = Form(...),
    released_date: date = Form(...),
    playtime_seconds: str | None = Form(None),
    db: Session = Depends(get_db),
    admin_user: models.User = Depends(require_admin_from_cookie)
):
    try:
        discography_in = schemas.DiscographyCreate(
            discography_title=discography_title,
            discography_num=int(discography_num) if discography_num else None,
            discography_type=discography_type,
            released_date=released_date,
            playtime_seconds= int(playtime_seconds) if playtime_seconds else None
        )
        crud.create_discography(db=db, discography=discography_in)
    except Exception as e:
        return templates.TemplateResponse(
            "discography_new.html", 
            {"request": request, "user": admin_user, "error": str(e)}
        )
        
    return RedirectResponse(
        url="/ui/discographies", status_code=303
    )
    
# 編集（管理者のみ）
@router.get("/discographies/{discography_id}/edit")
def edit_discography_page(
    discography_id: int,
    request: Request,
    db: Session = Depends(get_db),
    admin_user: models.User = Depends(require_admin_from_cookie)
):  
    print("HIT ui/discographies.py edit_discography_page", discography_id)

    discography = crud.get_discography(db=db, discography_id=discography_id)
    if discography is None:
        return templates.TemplateResponse(
            "discography_edit.html",
            {
                "request": request,
                "discography": None,
                "user": admin_user,
                "error": "対象のディスコグラフィが存在しません"
            }
        )
    return templates.TemplateResponse(
        "discography_edit.html",
        {"request": request, "discography": discography, "user": admin_user, "error": None}
    )
    
@router.post("/discographies/{discography_id}/edit")
def edit_discography_action(
    request: Request,
    discography_id: int, 
    db: Session = Depends(get_db),
    discography_title: str = Form(...),
    discography_type: str = Form(...),
    released_date: date = Form(...),
    discography_num: int = Form(...),
    playtime_seconds: Optional[int] = Form(None),   
    admin_user: models.User = Depends(require_admin_from_cookie)
):
    try: 
        crud.update_discography(
            db=db, 
            discography_id=discography_id,
            disco_update=schemas.DiscographyUpdate(
                discography_title=discography_title,
                discography_type=discography_type,
                released_date=released_date,
                discography_num=discography_num,
                playtime_seconds=playtime_seconds
            )
        )
        return RedirectResponse(url="/ui/discographies", status_code=303)
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
        
@router.post("/discographies/{discography_id}/delete")
def delete_discography_action(
    request: Request,
    discography_id: int,
    db: Session = Depends(get_db),
    admin_user: models.User = Depends(require_admin_from_cookie)
):
    try:
        crud.delete_discography(db=db, discography_id=discography_id)
        return RedirectResponse(url="/ui/discographies", status_code=303)
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