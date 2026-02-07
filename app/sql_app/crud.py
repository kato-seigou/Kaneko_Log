from typing import Optional

from sqlalchemy.orm import Session 
from fastapi import HTTPException, status

from . import models, schemas, security

# GET系
def get_users(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.User).order_by(models.User.user_id).offset(skip).limit(limit).all()

def get_discographies(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.Discography).order_by(models.Discography.released_date).offset(skip).limit(limit).all()

def get_logs(db: Session, user_id: Optional[int] = None, skip: int = 0, limit: int = 100):
    q = db.query(models.ListenLog)
    if user_id is not None:
        q = q.filter(models.ListenLog.user_id == user_id)
    return q.order_by(models.ListenLog.created_at.desc()).offset(skip).limit(limit).all()

# POST系
def create_user(db: Session, user: schemas.UserCreate):
    hashed = security.hash_password(user.password)
    
    # login_idの重複チェック
    db_user_registered = db.query(models.User).filter(models.User.login_id == user.login_id).first()
    if db_user_registered is not None:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=f"{user.login_id} is already used.")
    else:
        db_user = models.User(
            login_id = user.login_id,
            display_name = user.display_name, 
            password_hash = hashed
        )
        db.add(db_user)
        db.commit()
        db.refresh(db_user)
        return db_user

def create_discography(db: Session, discography: schemas.DiscographyCreate):
    db_discography_registered = db.query(models.Discography).filter(models.Discography.discography_title == discography.discography_title).first()
    if db_discography_registered is not None:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=f"{discography.discography_title} is already registered.")
    else:
        db_discography = models.Discography(
            discography_title = discography.discography_title,
            discography_num = discography.discography_num,
            discography_type = discography.discography_type,
            released_date = discography.released_date,
            playtime_seconds = discography.playtime_seconds
        )
        db.add(db_discography)
        db.commit()
        db.refresh(db_discography)
        return db_discography

def create_log(db: Session, user_id: int, log: schemas.ListenLogCreate):
    disco_existing = db.query(models.Discography).filter(models.Discography.discography_id == log.discography_id).first()
    if disco_existing is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="discography not found")
    else:
        db_log = models.ListenLog(
            user_id = user_id,
            discography_id = log.discography_id,
            comment = log.comment,
            listened_at = log.listened_at
        )
        db.add(db_log)
        db.commit()
        db.refresh(db_log)
        return db_log

# UPDATE
def update_log(db: Session, user_id: int, log_id: int, log_update: schemas.ListenLogUpdate):
    db_log = (
        db.query(models.ListenLog)
        .filter(models.ListenLog.log_id == log_id)
        .first()
    )
    if db_log is None or db_log.user_id != user_id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="log not found.")
    
    if log_update.comment is not None:
        db_log.comment = log_update.comment
    if log_update.listened_at is not None:
        db_log.listened_at = log_update.listened_at
        
    db.commit()
    db.refresh(db_log)
    return db_log

# DELETE
def delete_log(db: Session, user_id: int, log_id: int):
    db_log = (
        db.query(models.ListenLog)
        .filter(models.ListenLog.log_id == log_id)
        .first()
    )
    if db_log is None or db_log.user_id != user_id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="log not found.")
    
    db.delete(db_log)
    db.commit()
    return True