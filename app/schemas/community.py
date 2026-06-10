from pydantic import BaseModel, ConfigDict
from typing import Optional
from datetime import datetime


class DiscussionPostBase(BaseModel):
    title: str
    content_body: str
    category: Optional[str] = "GENERAL"


class DiscussionPostCreate(DiscussionPostBase):
    author_id: Optional[int] = None


class DiscussionPostUpdate(BaseModel):
    title: Optional[str] = None
    content_body: Optional[str] = None
    category: Optional[str] = None


class DiscussionPost(DiscussionPostBase):
    model_config = ConfigDict(from_attributes=True)
    id: int
    author_id: int
    created_at: datetime
    updated_at: datetime


class UpvoteBase(BaseModel):
    target_type: str
    target_id: int


class UpvoteCreate(UpvoteBase):
    user_id: Optional[int] = None


class Upvote(UpvoteBase):
    model_config = ConfigDict(from_attributes=True)
    id: int
    user_id: int
    created_at: datetime
