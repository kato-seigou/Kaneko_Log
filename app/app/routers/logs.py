from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from ..database import get_db
from .. import schemas, crud, security, models

router = APIRouter(prefix="/logs", tags=["logs"])

# ログの読み込み
@router.get("/", status_code=status.HTTP_200_OK, response_model=List[schemas.ListenLogRead])
def read_logs(current_user: models.User = Depends(security.get_current_user), db: Session = Depends(get_db),
              skip: int = 0, limit: int = 100):
    logs = crud.get_logs(db=db, user_id=current_user.user_id, skip=skip, limit=limit)
    return logs

# ログの作成
@router.post("/", status_code=status.HTTP_201_CREATED, response_model=schemas.ListenLogRead)
def create_log(
    log: schemas.ListenLogCreate, 
    current_user: models.User = Depends(security.get_current_user), 
    db: Session = Depends(get_db), 
               ):
    logs = crud.create_log(db=db, user_id=current_user.user_id, log=log)
    return logs

# ログの更新
@router.put("/{log_id}", response_model=schemas.ListenLogRead)
def update_log(
    log_id: int,
    log: schemas.ListenLogUpdate,
    current_user: models.User = Depends(security.get_current_user),
    db: Session = Depends(get_db)
):
    updated_log = crud.update_log(db=db, user_id=current_user.user_id, log_id=log_id, log_update=log)
    return updated_log

# ログの削除
@router.delete("/{log_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_log(
    log_id: int,
    current_user: models.User = Depends(security.get_current_user),
    db: Session = Depends(get_db)
):
    deleted_log = crud.delete_log(db=db, user_id=current_user.user_id, log_id=log_id)
    return deleted_log