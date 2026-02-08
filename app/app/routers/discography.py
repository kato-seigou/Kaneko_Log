from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from ..database import get_db
from .. import schemas, crud, security, models

router = APIRouter(prefix="/discographies", tags=["discographies"])

# ディスコグラフィの取得
# 全ログインユーザー対象
# ここはログインしなくても取得できる設計にしとく
@router.get("/", response_model=List[schemas.DiscographyRead])
def read_discographies(db: Session = Depends(get_db), skip: int = 0, limit: int = 100):
    discographies = crud.get_discographies(db=db, skip=skip, limit=limit)
    return discographies

# 管理者のみOK
@router.post("/", status_code=status.HTTP_201_CREATED, response_model=schemas.DiscographyRead)
def create_discography(
    discography: schemas.DiscographyCreate,
    admin_user: models.User = Depends(security.require_admin),
    db: Session = Depends(get_db)
):
    new_discography = crud.create_discography(db=db, discography=discography)
    return new_discography