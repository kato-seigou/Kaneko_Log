from __future__ import annotations

from fastapi import APIRouter, Request, HTTPException
from fastapi.responses import RedirectResponse

from .auth import COOKIE_NAME
from ._render import render
from ._deps import get_current_user_from_cookie

router = APIRouter(prefix="/ui", tags=["ui"])

@router.get("/")
def home_page(request: Request):
    try: 
        user = get_current_user_from_cookie(request)
        return RedirectResponse(url="/ui/logs", status_code=303)
    except HTTPException:
        pass
    
    return render(
        request=request,
        name="home.html",
        context={"user": None}
    )