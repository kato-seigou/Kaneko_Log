from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .database import Base, engine
from .routers import auth, discography, logs
from .routers.ui import auth as ui_auth
from .routers.ui import logs as ui_logs
from .routers.ui import discographies as ui_disco
from .routers.ui import timeline as ui_timeline

# DBテーブル作成
Base.metadata.create_all(bind=engine)

app = FastAPI(title="kanekoayano App API")

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

@app.get("/")
def root():
    return {
        "message": "kanekoayano App API",
        "docs": "/docs",
        "health": "/health",
    }


@app.get("/health")
def health():
    return {"status": "OK"}