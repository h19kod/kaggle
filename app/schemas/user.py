from pydantic import BaseModel, EmailStr, ConfigDict
from typing import Optional, List
from datetime import datetime


# User schemas
class UserBase(BaseModel):
    username: str
    email: EmailStr


class UserCreate(UserBase):
    password: str


class UserUpdate(BaseModel):
    username: Optional[str] = None
    email: Optional[EmailStr] = None
    password: Optional[str] = None
    global_tier: Optional[str] = None


class User(UserBase):
    model_config = ConfigDict(from_attributes=True)
    id: int
    created_at: datetime
    global_tier: str


# UserProfile schemas
class UserProfileBase(BaseModel):
    full_name: Optional[str] = None
    bio: Optional[str] = None
    github_url: Optional[str] = None
    linkedin_url: Optional[str] = None
    is_seeking_job: Optional[bool] = None


class UserProfileCreate(UserProfileBase):
    user_id: int


class UserProfileUpdate(UserProfileBase):
    pass


class UserProfile(UserProfileBase):
    model_config = ConfigDict(from_attributes=True)
    id: int
    user_id: int
    total_upvotes: int
