import datetime
from enum import Enum
from pydantic import BaseModel, Field, ConfigDict
from typing import Optional

# FastAPI側のデータ構造を定義する

### 認証関連
class Token(BaseModel):
    access_token: str
    token_type: str

### user関連
class UserBase(BaseModel):
    # UserCreateをUserReadで継承するとresに
    # passwordが含まれてしまう
    display_name: Optional[str] = Field(default=None, max_length=12)
    login_id: str = Field(max_length=12)
    
class UserCreate(UserBase):
    password: str = Field(min_length=8, max_length=72)
    
class UserRead(UserBase):
    # 表示用
    user_id: int
    created_at: datetime.datetime
    
    # pydantic: v2.8.2
    model_config = ConfigDict(from_attributes=True)
    
### discography関連
class DiscographyType(str, Enum):
    Album = "Album"
    EP = "EP"
    Single = "Single"
    Movie = "Movie"
    
class DiscographyCreate(BaseModel):
    discography_title: str = Field(min_length=1)
    discography_num: Optional[int] = Field(default=None, ge=1) # ディスコグラフィの収録曲数
    discography_type: DiscographyType
    released_date: datetime.date
    playtime_seconds: Optional[int] = Field(default=None, ge=1)
    
class DiscographyUpdate(BaseModel):
    discography_title: Optional[str] = Field(default=None, min_length=1)
    discography_num: Optional[int] = Field(default=None, ge=1)
    discography_type: Optional[DiscographyType] = None
    released_date: Optional[datetime.date] = None
    playtime_seconds: Optional[int] = Field(default=None, ge=1)

class DiscographyRead(DiscographyCreate):
    discography_id: int
    created_at: datetime.datetime

    model_config = ConfigDict(from_attributes=True)
    

### ログ関連
class ListenLogCreate(BaseModel):
    # user_id: int
    discography_id: int
    comment: Optional[str] = Field(default=None, max_length=50)
    listened_at: datetime.datetime
    
class ListenLogUpdate(BaseModel):
    discography_id: Optional[int] = None
    comment: Optional[str] = Field(default=None, max_length=50)
    listened_at: Optional[datetime.datetime] = None
    
class ListenLogRead(ListenLogCreate):
    log_id: int
    created_at: datetime.datetime
    deleted_at: Optional[datetime.datetime]
    
    model_config = ConfigDict(from_attributes=True)