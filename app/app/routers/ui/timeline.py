from fastapi import APIRouter, Request, Depends
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session

from ... import models, crud, schemas
from ... database import get_db
from ._templates import templates
from ._deps import get_current_user_from_cookie

router = APIRouter(prefix="/ui", tags=["tags"])

@router.get("/timeline")
def timeline_page(
    request: Request,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user_from_cookie),
    skip: int = 0,
    limit: int = 20
):
    logs = crud.get_timeline_logs(db=db, skip=skip, limit=limit)
    
    next_skip = skip + limit
    has_more = len(logs) == limit
    
    return templates.TemplateResponse(
        "timeline.html",
        {
            "request": request,
            "user": current_user,
            "logs": logs,
            "skip": skip,
            "limit": limit,
            "next_skip": next_skip,
            "has_more": has_more
        }
    )