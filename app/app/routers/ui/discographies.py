from __future__ import annotations

from fastapi import APIRouter, Request, Depends, Form
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session
from datetime import datetime, date

from ... database import get_db
from ... import crud, models, schemas
from ._templates import templates
from ._deps import get_current_user_from_cookie, require_admin_from_cookie

router = APIRouter(prefix="/ui", tags=["ui"])

# ディスコグラフィ一覧表示
@router.get("/discographies")
def discographies_page(
    request: Request,
    db: Session = Depends(get_db)
):
    discographies = crud.get_discographies(db=db)
    return templates.TemplateResponse(
        "discographies.html",
        {"request": request, "discographies": discographies}
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
    discography_num: str | None = Form(None),
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