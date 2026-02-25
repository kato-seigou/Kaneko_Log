from pathlib import Path
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse, HTMLResponse
from fastapi.exceptions import HTTPException
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from starlette.exceptions import HTTPException as StarletteHTTPException
from starlette.status import HTTP_404_NOT_FOUND, HTTP_401_UNAUTHORIZED


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
from .routers.ui import stats as ui_stats

# DBテーブル作成
# Base.metadata.create_all(bind=engine)

app = FastAPI(title="kanekoayano App API")

# css
BASE_DIR = Path(__file__).resolve().parent
STATIC_DIR = BASE_DIR / "static"
TEMPLATES_DIR = BASE_DIR / "templates"
app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")
templates = Jinja2Templates(directory=str(TEMPLATES_DIR))

# app.add_middleware(
#     CORSMiddleware,
#     allow_origins=["*"],
#     allow_credentials=True,
#     allow_methods=["*"],
#     allow_headers=["*"]
# )

app.include_router(auth.router)
app.include_router(discography.router)
app.include_router(logs.router)
app.include_router(ui_auth.router)
app.include_router(ui_logs.router)
app.include_router(ui_disco.router)
app.include_router(ui_timeline.router)
app.include_router(ui_account.router)
app.include_router(ui_stats.router)

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

@app.exception_handler(StarletteHTTPException)
async def http_exception_handler(request: Request, exc: StarletteHTTPException):
    token = request.cookies.get(auth.COOKIE_NAME)
    logged_in = bool(token)
    
    if exc.status_code == HTTP_401_UNAUTHORIZED:
        return templates.TemplateResponse(
            "errors/401.html",
            {"request": request, "logged_in": logged_in},
            status_code=HTTP_401_UNAUTHORIZED,
        )
    
    if exc.status_code == HTTP_404_NOT_FOUND:
        return templates.TemplateResponse(
            "errors/404.html",
            {"request": request, "logged_in": logged_in},
            status_code=HTTP_404_NOT_FOUND,
        )
    
    return templates.TemplateResponse(
        "errors/errors.html",
        {"request": request, "logged_in": logged_in, "status_code": exc.status_code},
        status_code=exc.status_code
    )

@app.exception_handler(Exception)
async def unhandled_exception_handler(request: Request, exc: Exception):
    token = request.cookies.get(auth.COOKIE_NAME)
    logged_in = bool(token)
    
    return templates.TemplateResponse(
        "errors/errors.html",
        {"request": request, "logged_in": logged_in, "status_code": 500},
        status_code=500,
    )