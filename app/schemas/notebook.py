from pydantic import BaseModel, ConfigDict
from typing import Optional
from datetime import datetime


class NotebookBase(BaseModel):
    title: str
    description: Optional[str] = None
    language: Optional[str] = "python"
    storage_path_url: Optional[str] = None


class NotebookCreate(NotebookBase):
    creator_id: Optional[int] = None
    forked_from_id: Optional[int] = None


class NotebookUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    language: Optional[str] = None
    storage_path_url: Optional[str] = None


class Notebook(NotebookBase):
    model_config = ConfigDict(from_attributes=True)
    id: int
    creator_id: int
    forked_from_id: Optional[int] = None
    created_at: datetime
    updated_at: datetime


class ComputeSessionBase(BaseModel):
    hardware_target: Optional[str] = "CPU"
    notebook_id: Optional[int] = None


class ComputeSessionCreate(ComputeSessionBase):
    user_id: int


class ComputeSession(ComputeSessionBase):
    model_config = ConfigDict(from_attributes=True)
    id: int
    user_id: int
    container_id: Optional[str] = None
    session_status: str
    start_time: datetime
    end_time: Optional[datetime] = None
    allowed_quota_remaining_minutes: int
