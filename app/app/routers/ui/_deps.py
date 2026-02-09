# UI側のログイン必須を実装
### つまり、Dependencyの実装
# Cookie -> current_user
# security.get_current_userはOAuth2依存なので、UIように別Dependencyを用意する
from __future__ import annotations

from fastapi import Depends, HTTPException, Request, status
from sqlalchemy.orm import Session
from jose import JWTError

from ...database import get_db
from ... import models, security

COOKIE_NAME = "access_token"

def get_current_user_from_cookie(
    request: Request,
    db: Session = Depends(get_db),
) -> models.User:
    token = request.cookies.get(COOKIE_NAME)
    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authenticated"
        )
    try:
        payload = security.decode_access_token(token)
        sub = payload.get("sub")
        if sub is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid Token"
            )
        user_id = int(sub)
    except (JWTError, ValueError, TypeError):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid Token"
        )
        
    user = db.query(models.User).filter(models.User.user_id == user_id).first()
    if user is None:
        return HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found")
    
    return user

def require_admin_from_cookie(
    current_user: models.User = Depends(get_current_user_from_cookie)
) -> models.User:
    if not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin privileges required"
        )
    return current_user