from typing import Annotated
from fastapi import APIRouter, status, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session 

from ..database import get_db
from .. import schemas, crud, security, models

# models.Base.metadata.create_all(bind=engine)

router = APIRouter(prefix="/auth", tags=["auth"])

# ユーザー登録
@router.post("/register", status_code=status.HTTP_201_CREATED, response_model=schemas.UserRead)
def create_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    return crud.create_user(db=db, user=user)

# ログイン
@router.post("/login", status_code=status.HTTP_200_OK, response_model=schemas.Token)
def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = security.authenticate_user(
        login_id=form_data.username, 
        password=form_data.password, 
        db=db)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password.",
            headers={"WWW-Authenticate": "Bearer"}
        )
    access_token = security.create_access_token(
        data={"sub": str(user.user_id)}, 
        # expires_delta=60(default) 
    )

    return {
        "access_token": access_token,
        "token_type": "bearer"
    }

# ログアウト
@router.post("/logout", status_code=status.HTTP_204_NO_CONTENT)
def logout(current_user: models.User = Depends(security.get_current_user)):
    return 