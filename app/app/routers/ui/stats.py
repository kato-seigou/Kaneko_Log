from __future__ import annotations

from typing import List, Optional
from datetime import datetime, date, time
from fastapi import APIRouter, Request, Depends, Form, HTTPException, Query
from fastapi.responses import RedirectResponse, HTMLResponse
from sqlalchemy.orm import Session
from urllib.parse import unquote
from fastapi.responses import JSONResponse

from ... import models, crud, schemas
from ...database import get_db
from ._templates import templates
from ._deps import get_current_user_from_cookie, get_current_user_from_cookie_optional
from ._render import render
from ._csrf import ensure_csrf_token, validate_csrf
from ._flash import redirect_with_flash, add_flash, FLASH_SUCCESS, FLASH_ERROR, FLASH_INFO

router = APIRouter(prefix="/ui", tags=["ui"])

@router.get("/stats")
def stats_page(
    request: Request,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user_from_cookie_optional)
):
    if current_user is None:
        resp = RedirectResponse(url="/ui/login", status_code=303)
        return add_flash(resp, "ログインしてください", level=FLASH_INFO)
    
    # KPI
    # 総ログ数
    play_counts = crud.get_discography_play_counts(db=db, user_id=current_user.user_id)
    total_counts = sum([row[3] for row in play_counts])
    # 初回投稿日、経過日数
    first_log_date, elapsed_days = crud.get_first_log_date(db=db, user_id=current_user.user_id)
    
    # overview（ディスコグラフィ別再生回数）
    # total_logsをそのまま流用
    
    # rate（Album + EPの割合）
    shares_ratio = crud.get_discography_share(db=db, user_id=current_user.user_id)
    
    # 今月の月別
    now = datetime.now()
    year, month = now.year, now.month
    monthly_counts = crud.get_monthly_discography_counts(db=db, year=year, month=month, user_id=current_user.user_id)
    
    return render(
        request=request,
        name="stats.html",
        context={
            "user": current_user,
            "play_counts": play_counts, # 各ディスコグラフィごとの再生回数
            "first_log_date": first_log_date, # 初回投稿日
            "elapsed_days": elapsed_days, # 経過日数
            "total_counts": total_counts, # 総ログ数
            "shares_ratio": shares_ratio, # ディスコグラフィごとの割合（EP・アルバムのみ）
            "year": year,
            "month": month,
            "monthly_counts": monthly_counts
        }
    )

@router.get("/stats/monthly", response_class=HTMLResponse)
def stats_monthly_partial(
    request: Request,
    year: int,
    month: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user_from_cookie_optional)
):
    if current_user is None:
        resp = RedirectResponse(url="/ui/login", status_code=303)
        return add_flash(resp, "ログインしてください", level=FLASH_INFO)
    
    monthly_counts = crud.get_monthly_discography_counts(
        db=db, year=year, month=month, user_id=current_user.user_id
    )
    
    return templates.TemplateResponse(
        "partials/_monthly_stats.html",
        {
            "request": request,
            "year": year,
            "month": month,
            "monthly_counts": monthly_counts
        }
    )

@router.get("/stats/pie")
def stats_pie(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user_from_cookie_optional),
):
    if current_user is None:
        return JSONResponse(status_code=401, content={"detail": "Unauthorized"})

    rows = crud.get_discography_play_counts(db=db, user_id=current_user.user_id)

    DTYPES = ["Album", "EP", "Single", "Movie"]

    grouped: dict[str, list[tuple[str, int]]] = {}
    for row in rows:
        dtype = row[2]
        dtype = dtype.value if hasattr(dtype, "value") else dtype  # Enum対策
        title = row[1]
        count = row[3]
        grouped.setdefault(dtype, []).append((title, count))

    inner_labels, inner_data = [], []
    for dtype in DTYPES:
        s = sum(count for _, count in grouped.get(dtype, []))
        if s > 0:
            inner_labels.append(dtype)
            inner_data.append(s)

    outer_labels, outer_data = [], []
    for dtype in DTYPES:
        for title, count in grouped.get(dtype, []):
            outer_labels.append(title)
            outer_data.append(count)

    return {
        "inner": {"labels": inner_labels, "data": inner_data},
        "outer": {"labels": outer_labels, "data": outer_data},
    }