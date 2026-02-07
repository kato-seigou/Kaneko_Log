# パスワードhash/verify + JWT関連
from __future__ import annotations

import os 
from datetime import datetime, timedelta, timezone
from typing import Any, Optional

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from passlib.context import CryptContext
from sqlalchemy.orm import Session

from .database import get_db
from . import models

# 設定
# TODO この辺一切わからない
SECRET_KEY = os.getenv("SECRET_KEY", "CHANGE_ME__SET__ENV_SECRET_KEY")
ALGORITHM = os.getenv("JWT_ALGORITHM", "HS256")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "60"))

if SECRET_KEY == "CHANGE_ME__SET_ENV_SECRET_KEY":
    pass

# パスワード関連
# ハッシュ化と認証
pwd_context = CryptContext(
    schemes=["bcrypt"], deprecated="auto"
)

def hash_password(plain_password: str) -> str:
    # 平文パスワードをハッシュ化して返す（DB保存用）
    return pwd_context.hash(plain_password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    # 平文パスワードが、保存済みハッシュと一致するか検証
    return pwd_context.verify(plain_password, hashed_password)

# JWT（トークン）
def create_access_token(
    data: dict[str, Any],
    expires_delta: Optional[timedelta] = None,
) -> str:
    # JWTを作成して返す
    to_encode = data.copy()
    
    expire = datetime.now(timezone.utc) + (
        expires_delta if expires_delta is not None else timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    )
    to_encode.update({"exp": expire})
    
    encode_jwt = jwt.encode(to_encode, algorithm=ALGORITHM)
    return encode_jwt

def decode_access_token(token: str) -> dict[str, Any]:
    # JWTをデコード
    payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    return payload

# FastAPI依存: ログインユーザー取得
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")

def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
) -> models.User:
    """
    Authorization: Bearer <token>からユーザーを確定して返す
    - トークン検証
    - sub（user_id想定）を取り出す
    - DBからUserを取得
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"}
    )

    try:
        payload = decode_access_token(token)
        sub = payload.get("sub")
        if sub is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    
    try:
        user_id = int(sub)
    except (TypeError, ValueError):
        raise credentials_exception
    
    user = db.query(models.User).filter(models.User.user_id == user_id).first()
    if user is None:
        raise credentials_exception
    return user


