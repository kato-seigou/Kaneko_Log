# データの構造を書く
from datetime import datetime
from sqlalchemy import (Column, ForeignKey, Integer, String, DateTime)
from .database import Base

class User(Base):
    __tablename__ = "users"
    user_id = Column(Integer, primary_key=True, index=True)
    login_id = Column(String(10), nullable=False, unique=True)
    display_name = Column(String(12), nullable=True, unique=False, index=True)
    password_hash = Column(String, nullable=False, unique=False)
    created_at = Column(DateTime, nullable=False, unique=False, default=datetime.utcnow)
    
