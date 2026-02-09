from __future__ import annotations

from datetime import datetime
from fastapi import APIRouter, Request, Depends, Form, HTTPException
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session

from ... import models, crud, schemas
from ... database import get_db
from ._templates import templates
from ._deps import get_current_user_from_cookie

router = APIRouter(prefix="/ui", tags=["ui"])

@router.get("/logs")
def logs_page(
    request: Request,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user_from_cookie),
    skip: int = 0,
    limit: int = 100
):
    logs = crud.get_logs(
        db=db, user_id=current_user.user_id, skip=skip, limit=limit
    )
    return templates.TemplateResponse(
        "logs.html",
        {"request": request, "user": current_user, "logs": logs}
    )
    
@router.get("/logs/new")
def new_log_page(
    request: Request,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user_from_cookie)
):
    discographies = crud.get_discographies(db=db)
    
    return templates.TemplateResponse(
        "log_new.html",
        {
            "request": request, 
            "user": current_user, 
            "discographies": discographies,
            "now": datetime.now()}
    )
    
@router.get("/logs/{log_id}/edit")
def edit_log_page(
    log_id: int,
    request: Request,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user_from_cookie)
):
    log = crud.get_log(db=db, user_id=current_user.user_id, log_id=log_id)
    discographies = crud.get_discographies(db=db)
    
    return templates.TemplateResponse(
        "log_edit.html",
        {
            "request": request,
            "user": current_user,
            "log": log,
            "discographies": discographies,
            "error": None,
            "now": datetime.now()
        }
    )
    
@router.post("/logs/new")
def create_log_action(
    request: Request,
    current_user: models.User = Depends(get_current_user_from_cookie),
    discography_id: int = Form(...),
    comment: str | None = Form(None),
    listened_at: datetime = Form(...),
    db: Session = Depends(get_db)
):
    crud.create_log(
        db=db,
        user_id=current_user.user_id,
        log=schemas.ListenLogCreate(
            discography_id=discography_id,
            comment=comment,
            listened_at=listened_at
        )
    )
    return RedirectResponse(
        url="/ui/logs", status_code=303
    )
    
@router.post("/logs/{log_id}/edit")
def edit_log_action(
    log_id: int,
    request: Request,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user_from_cookie),
    discography_id: int = Form(...),
    comment: str | None = Form(None),
    listened_at: datetime = Form(...)
):
    comment = comment if (comment is not None and comment.strip() != "") else None
    
    crud.update_log(
        db=db,
        user_id=current_user.user_id,
        log_id=log_id,
        log_update=schemas.ListenLogUpdate(
            discography_id=discography_id,
            comment=comment,
            listened_at=listened_at
        )
    )
    return RedirectResponse(url="/ui/logs", status_code=303)

@router.post("/logs/{log_id}/delete")
def delete_log_action(
    log_id: int,
    request: Request,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user_from_cookie)
):
    crud.delete_log(db=db, user_id=current_user.user_id, log_id=log_id)
    return RedirectResponse(url="/ui/logs", status_code=303)