import os
from pathlib import Path
from dotenv import load_dotenv

# .envを読み取る
# .envにある定数を環境変数としてos.getenv()で取得する
ENV_PATH = Path(__file__).resolve().parents[2] / ".env"
load_dotenv(ENV_PATH)

# JWT（トークン）に署名するときの秘密鍵
SECRET_KEY = os.getenv("SECRET_KEY")
if not SECRET_KEY:
    raise RuntimeError("SECRET_KEY is not set. Please set SECRET_KEY env var.")

# JWTを署名するときの署名アルゴリズム
ALGORITHM = os.getenv("JWT_ALGORITHM", "HS256")

# ログイン状態（アクセストークン）の有効期限（分）
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "60"))

ENV = os.getenv("ENV", "development")
SECURE_COOKIE = (ENV == "production") # ENVが"production"ならTrueを返す