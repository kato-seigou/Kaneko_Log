# データベース側の構造を書く
from datetime import datetime, timezone
from sqlalchemy import (Column, ForeignKey, Integer, String, DateTime, Date, Boolean)
from .database import Base
from sqlalchemy.orm import relationship

class User(Base):
    __tablename__ = "users"
    user_id = Column(Integer, primary_key=True, index=True)
    login_id = Column(String(10), nullable=False, unique=True, index=True)
    display_name = Column(String(12), nullable=True, unique=False, index=True)
    password_hash = Column(String, nullable=False, unique=False)
    created_at = Column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc)
    )
    is_admin = Column(Boolean, nullable=False, default=False)
    
    logs = relationship("ListenLog", back_populates="user")
    
class Discography(Base):
    __tablename__ = "discographies"
    discography_id = Column(Integer, primary_key=True)
    discography_title = Column(String, nullable=False, unique=True, index=True)
    discography_num = Column(Integer, nullable=False, unique=False)
    discography_type = Column(String, nullable=False, unique=False)
    released_date = Column(Date, nullable=False, unique=False)
    playtime_seconds = Column(Integer, nullable=False, unique=False)
    created_at = Column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc)
    )
    
    logs = relationship("ListenLog", back_populates="discography")
    
class ListenLog(Base):
    __tablename__ = "listen_logs"
    log_id = Column(Integer, primary_key=True)
    user_id = Column(
        Integer, 
        ForeignKey("users.user_id", ondelete="CASCADE"), 
        nullable=False
                     )
    discography_id = Column(
        Integer, 
        ForeignKey("discographies.discography_id", ondelete="RESTRICT"), 
        nullable=False
        )
    comment = Column(String(50), nullable=True, unique=False)
    listened_at = Column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc)
    )
    created_at = Column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc)
    )
    deleted_at = Column(DateTime(timezone=True), nullable=True)
    
    discography = relationship("Discography", back_populates="logs")
    user = relationship("User", back_populates="logs")