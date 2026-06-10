from enum import Enum as PyEnum
from sqlalchemy import Column, Integer, String, DateTime, Text, ForeignKey, Boolean, Table, Enum
from sqlalchemy.orm import relationship
from datetime import datetime, timezone
from app.core.database import Base


dataset_notebook_links = Table(
    "dataset_notebook_links",
    Base.metadata,
    Column("notebook_id", Integer, ForeignKey("notebooks.id"), primary_key=True),
    Column("dataset_id", Integer, ForeignKey("datasets.id"), primary_key=True),
)


class DatasetStatus(PyEnum):
    PENDING = "Pending"
    ACTIVE = "Active"


class Dataset(Base):
    __tablename__ = "datasets"

    id = Column(Integer, primary_key=True, index=True)
    owner_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    title = Column(String(200), nullable=False)
    slug = Column(String(200), unique=True, index=True, nullable=False)
    description = Column(Text, nullable=True)
    status = Column(Enum(DatasetStatus), default=DatasetStatus.PENDING)
    is_public = Column(Boolean, default=True)
    views_count = Column(Integer, default=0)
    downloads_count = Column(Integer, default=0)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

    owner = relationship("User", back_populates="datasets")
    files = relationship("DatasetFile", back_populates="dataset")
    linked_notebooks = relationship(
        "Notebook",
        secondary=dataset_notebook_links,
        back_populates="linked_datasets",
    )


class DatasetFile(Base):
    __tablename__ = "dataset_files"

    id = Column(Integer, primary_key=True, index=True)
    dataset_id = Column(Integer, ForeignKey("datasets.id"), nullable=False)
    file_name = Column(String(255), nullable=False)
    storage_path_url = Column(String(500), nullable=False)
    file_size_bytes = Column(Integer, nullable=True)
    file_type = Column(String(50), nullable=True)

    dataset = relationship("Dataset", back_populates="files")
