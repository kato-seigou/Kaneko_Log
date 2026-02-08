from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .database import Base, engine
from .routers import auth, discography, logs

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