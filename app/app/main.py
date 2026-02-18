from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse, HTMLResponse
from fastapi.exceptions import HTTPException
from starlette.status import HTTP_404_NOT_FOUND
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles

from .database import Base, engine
from .routers.ui._render import render
from .routers.ui._deps import get_current_user_from_cookie
from .routers import auth, discography, logs
from .routers.ui import _deps
from .routers.ui import auth as ui_auth
from .routers.ui import auth
from .routers.ui import logs as ui_logs
from .routers.ui import discographies as ui_disco
from .routers.ui import timeline as ui_timeline
from .routers.ui import account as ui_account

# DBテーブル作成
# Base.metadata.create_all(bind=engine)

app = FastAPI(title="kanekoayano App API")

app.mount("/static", StaticFiles(directory="app/app/static"), name="static")

templates = Jinja2Templates(directory="app/app/templates")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

app.include_router(auth.router)
app.include_router(discography.router)
app.include_router(logs.router)
app.include_router(ui_auth.router)
app.include_router(ui_logs.router)
app.include_router(ui_disco.router)
app.include_router(ui_timeline.router)
app.include_router(ui_account.router)

# @app.get("/")
# def root():
#     return RedirectResponse(url="/ui/login", status_code=303)
@app.get("/")
def home_page(request: Request):
    token = request.cookies.get(auth.COOKIE_NAME)
    if token:
        return RedirectResponse(url="/ui/logs", status_code=303)
    return render(
        request=request,
        name="home.html",
        context={"user": None}
    )

@app.get("/health")
def health():
    return {"status": "OK"}

@app.exception_handler(404)
async def custom_404_handler(request: Request, exc: HTTPException):
    token = request.cookies.get(auth.COOKIE_NAME)
    logged_in = bool(token)
        
    return templates.TemplateResponse(
        "404.html",
        {"request": request, "logged_in": logged_in},
        status_code=HTTP_404_NOT_FOUND,
    )
    
@app.exception_handler(401)
async def custom_401_handler(request: Request, exc: HTTPException):
    token = request.cookies.get(auth.COOKIE_NAME)
    logged_in = bool(token)
    
    return templates.TemplateResponse(
        "404.html",
        {"request": request, "logged_in": logged_in},
        status_code=HTTP_404_NOT_FOUND,
    )