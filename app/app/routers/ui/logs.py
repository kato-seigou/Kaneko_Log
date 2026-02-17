from __future__ import annotations

from typing import List, Optional
from datetime import datetime, date, time
from fastapi import APIRouter, Request, Depends, Form, HTTPException, Query
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session
from urllib.parse import unquote

from ... import models, crud, schemas
from ... database import get_db
from ._templates import templates
from ._deps import get_current_user_from_cookie, get_current_user_from_cookie_optional
from ._render import render
from ._csrf import ensure_csrf_token, validate_csrf
from ._flash import redirect_with_flash, add_flash, FLASH_SUCCESS, FLASH_ERROR, FLASH_INFO

router = APIRouter(prefix="/ui", tags=["ui"])

@router.get("/logs")
def logs_page(
    request: Request,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user_from_cookie_optional),
    skip: int = 0,
    limit: int = 5,
):
    
    if current_user is None:
        resp = RedirectResponse(url="/ui/login", status_code=303)
        return add_flash(resp, "ログインしてください", level=FLASH_INFO)
    
    logs_plus = crud.get_logs(
        db=db, user_id=current_user.user_id, skip=skip, limit=limit + 1
    )
    
    # limitよりもlogs_plusが大きければ次ページがあると言える
    has_next = len(logs_plus) > limit
    logs = logs_plus[:limit]
    
    return render(
        request=request, 
        name="logs.html", 
        context={"user": current_user, "logs": logs, "skip": skip, "limit": limit, "has_next": has_next}
    )

@router.get("/logs/search")
def search_logs_page(
    request: Request,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user_from_cookie),
    start_period: date | None = Query(None),
    end_period: date | None = Query(None),
    search_title: List[str] | None = Query(None),
    search_type: List[str] | None = Query(None),
    skip: int = Query(0),
    limit: int = Query(2),
):
    print("DEBUG", start_period, end_period, search_title, search_type, skip, limit)

    if current_user is None:
        resp = RedirectResponse(url="/ui/login", status_code=303)
        return add_flash(resp, "ログインしてください", level=FLASH_INFO)
    
    discographies = crud.get_discographies(db=db)
    
    # datetime型に変換する
    if start_period:
        start_period = datetime.combine(start_period, time.min)
    if end_period:
        end_period = datetime.combine(end_period, time.max)
    
    log_plus = crud.search_logs(
        db=db,
        user_id=current_user.user_id,
        start_period=start_period,
        end_period=end_period,
        search_title=search_title,
        search_type=search_type,
        skip=skip,
        limit=limit + 1,
    )
    
    has_next = len(log_plus) > limit
    logs = log_plus[:limit]
    
    return render(
        request=request,
        name="log_search.html",
        context={
            "user": current_user,
            "discographies": discographies,
            "limit": limit,
            "date_now": datetime.today().date(),
            # 検索のパラメータ
            "start_period": start_period,
            "end_period": end_period,
            "search_title": search_title,
            "search_type": search_type,
            "logs": logs,
            "skip": skip,
            "has_next": has_next
        },
    )

@router.get("/logs/new")
def new_log_page(
    request: Request,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user_from_cookie)
):
    discographies = crud.get_discographies(db=db)
    
    return render(
        request=request,
        name="log_new.html",
        context={
            "user": current_user,
            "discographies": discographies,
            "now": datetime.now()
        }
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
    return render(
        request=request,
        name="log_edit.html",
        context={
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
    db: Session = Depends(get_db),
    csrf_token: str = Form(...)
):
    validate_csrf(request, csrf_token)
    try: 
        crud.create_log(
            db=db,
            user_id=current_user.user_id,
            log=schemas.ListenLogCreate(
                discography_id=discography_id,
                comment=comment,
                listened_at=listened_at
            )
        )
    except Exception:
        return redirect_with_flash(
            "/ui/logs",
            "ログの作成に失敗しました。",
            level=FLASH_ERROR
        )
    return redirect_with_flash(
        "/ui/logs",
        "ログを追加しました。",
        level=FLASH_SUCCESS
    )
    
@router.post("/logs/{log_id}/edit")
def edit_log_action(
    log_id: int,
    request: Request,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user_from_cookie),
    discography_id: int = Form(...),
    comment: str | None = Form(None),
    listened_at: datetime = Form(...),
    csrf_token: str = Form(...)
):
    validate_csrf(request, csrf_token)
    
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
    # return RedirectResponse(url="/ui/logs", status_code=303)
    return redirect_with_flash(
        url="/ui/logs",
        message="ログを編集しました",
        level=FLASH_SUCCESS
    )

@router.post("/logs/{log_id}/delete")
def delete_log_action(
    log_id: int,
    request: Request,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user_from_cookie),
    csrf_token: str = Form(...)
):
    validate_csrf(request, csrf_token)
    
    crud.delete_log(db=db, user_id=current_user.user_id, log_id=log_id)
    # return RedirectResponse(url="/ui/logs", status_code=303)
    return redirect_with_flash(
        url="/ui/logs",
        message="ログを削除しました",
        level=FLASH_ERROR
    )
    
# @router.post("/logs/search")
# def search_log_action(
#     request: Request,
#     db: Session = Depends(get_db),
#     current_user: models.User = Depends(get_current_user_from_cookie),
#     start_period: Optional[datetime] = Form(None),
#     end_period: Optional[datetime] = Form(None),
#     search_title: Optional[List[str]] = Form(None),
#     search_type: Optional[List[str]] = Form(None),
#     skip: int = 0,
#     limit: int = 2,
# ):
#     if current_user is None:
#         resp = RedirectResponse(url="/ui/login", status_code=303)
#         return add_flash(resp, "ログインしてください", level=FLASH_INFO)
    
#     discographies = crud.get_discographies(db=db)
    
#     log_plus = crud.search_logs(
#         db=db,
#         user_id=current_user.user_id,
#         start_period=start_period,
#         end_period=end_period,
#         search_title=search_title,
#         search_type=search_type,
#         skip=skip,
#         limit=limit + 1
#     )
    
#     has_next = len(log_plus) > limit
#     logs = log_plus[:limit]
    
#     error = None
#     if not logs and skip == 0:
#         error ="対照のログが存在しません"

#     return render(
#         request=request,
#         name="log_search.html",
#         context={
#             "user": current_user,
#             "discographies": discographies,
#             "logs": logs,
#             "skip": skip,
#             "limit": limit,
#             "has_next": has_next,
#             "date_now": datetime.today().date(),
#             "start_period": start_period,
#             "end_period": end_period,
#             "search_title": search_title or [],
#             "search_type": search_type or [],
#             "error": error,
#         }
#     )