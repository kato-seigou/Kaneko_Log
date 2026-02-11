from typing import Optional

from sqlalchemy.orm import Session , joinedload
from sqlalchemy.exc import IntegrityError
from fastapi import HTTPException, status

from . import models, schemas, security

# ここでDBの操作を行う

# GET系
def get_users(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.User).order_by(models.User.user_id).offset(skip).limit(limit).all()

def get_discography(db: Session, discography_id: int):
    disco = db.query(models.Discography).filter(models.Discography.discography_id == discography_id).first()
    return disco

def get_discographies(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.Discography).order_by(models.Discography.released_date).offset(skip).limit(limit).all()

# 複数取得用
def get_logs(db: Session, user_id: Optional[int] = None, skip: int = 0, limit: int = 100):
    """複数取得用"""
    q = db.query(models.ListenLog)
    if user_id is not None:
        q = q.filter(models.ListenLog.user_id == user_id)
    return q.order_by(models.ListenLog.created_at.desc()).offset(skip).limit(limit).all()

# 1件取得用
def get_log(db: Session, user_id: int, log_id: int):
    """1件取得用"""
    db_log = db.query(models.ListenLog).filter(models.ListenLog.log_id == log_id, models.ListenLog.user_id == user_id).first()
    if db_log is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="ログが見つかりませんでした")
    return db_log

# タイムライン用の取得関数
def get_timeline_logs(db: Session, skip: int = 0, limit: int = 20):
    q = (
        db.query(models.ListenLog)
        .options(
            joinedload(models.ListenLog.user),
            joinedload(models.ListenLog.discography)
        )
        .filter(models.ListenLog.deleted_at.is_(None))
        .order_by(models.ListenLog.listened_at.desc(), models.ListenLog.created_at.desc())
        .offset(skip)
        .limit(limit)
    )
    return q.all()

# POST系
def create_user(db: Session, user: schemas.UserCreate):
    hashed = security.hash_password(user.password)
    
    # login_idの重複チェック
    db_user_registered = db.query(models.User).filter(models.User.login_id == user.login_id).first()
    if db_user_registered is not None:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=f"このログインID（@{user.login_id}）はすでに使われています。")
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
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="ディスコグラフィが見つかりませんでした")
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
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="ログが見つかりませんでした")
    
    if log_update.discography_id is not None:
        disco = db.query(models.Discography).filter(models.Discography.discography_id == log_update.discography_id).first()
        if disco is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="ディスコグラフィが見つかりませんでした")
        db_log.discography_id = log_update.discography_id
        
    
    if log_update.comment is not None:
        db_log.comment = log_update.comment
    if log_update.listened_at is not None:
        db_log.listened_at = log_update.listened_at
        
    db.commit()
    db.refresh(db_log)
    return db_log

def update_discography(db: Session, discography_id: int, disco_update: schemas.DiscographyUpdate):
    disco = get_discography(db, discography_id)
    
    if disco is None:
        raise HTTPException(status_code=404, detail="ディスコグラフィが見つかりませんでした")
    
    if disco_update.discography_title is not None:
        exists = db.query(models.Discography).filter(
            models.Discography.discography_title == disco_update.discography_title,
            models.Discography.discography_id != discography_id
        ).first()
        if exists:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="このタイトルのディスコグラフィは既に存在します")
        disco.discography_title = disco_update.discography_title
        
    if disco_update.discography_num is not None:
        disco.discography_num = disco_update.discography_num
    if disco_update.discography_type is not None:
        disco.discography_type = disco_update.discography_type
    if disco_update.released_date is not None:
        disco.released_date = disco_update.released_date
    if disco_update.playtime_seconds is not None:
        disco.playtime_seconds = disco_update.playtime_seconds

    db.commit()
    db.refresh(disco)
    return disco

# DELETE
def delete_log(db: Session, user_id: int, log_id: int):
    db_log = (
        db.query(models.ListenLog)
        .filter(models.ListenLog.log_id == log_id)
        .first()
    )
    if db_log is None or db_log.user_id != user_id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="ログが見つかりませんでした")
    
    db.delete(db_log)
    db.commit()
    return True

def delete_discography(db: Session, discography_id: int):
    disco = get_discography(db, discography_id)
    if disco is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="ディスコグラフィが見つかりませんでした"
        )

    try:
        db.delete(disco)
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="このディスコグラフィはすでにログで参照されているため、削除することができません"
        )
    return True