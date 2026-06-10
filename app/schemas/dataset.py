from pydantic import BaseModel, ConfigDict
from typing import Optional, List
from datetime import datetime


class DatasetFileBase(BaseModel):
    file_name: str
    storage_path_url: str
    file_size_bytes: Optional[int] = None
    file_type: Optional[str] = None


class DatasetFileCreate(DatasetFileBase):
    dataset_id: int


class DatasetFile(DatasetFileBase):
    model_config = ConfigDict(from_attributes=True)
    id: int
    dataset_id: int


class DatasetBase(BaseModel):
    title: str
    slug: str
    description: Optional[str] = None
    status: Optional[str] = "Pending"
    is_public: Optional[bool] = True


class DatasetCreate(DatasetBase):
    owner_id: int


class DatasetUpdate(BaseModel):
    title: Optional[str] = None
    slug: Optional[str] = None
    description: Optional[str] = None
    is_public: Optional[bool] = None


class Dataset(DatasetBase):
    model_config = ConfigDict(from_attributes=True)
    id: int
    owner_id: int
    views_count: int
    downloads_count: int
    status: str
    created_at: datetime
    updated_at: datetime
    files: Optional[List[DatasetFile]] = None
