from sqlalchemy import Column, Integer, String, DateTime, Text, ForeignKey, Enum
from sqlalchemy.orm import relationship
from datetime import datetime, timezone
from enum import Enum as PyEnum
from app.core.database import Base


class ComputeHardware(PyEnum):
    CPU = "CPU"
    GPU = "GPU"
    TPU = "TPU"


class SessionStatus(PyEnum):
    ACTIVE = "Active"
    IDLE = "Idle"
    TERMINATED = "Terminated"


class Notebook(Base):
    __tablename__ = "notebooks"

    id = Column(Integer, primary_key=True, index=True)
    creator_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    title = Column(String(200), nullable=False)
    description = Column(Text, nullable=True)
    language = Column(String(20), default="python")
    storage_path_url = Column(String(500), nullable=True)
    forked_from_id = Column(Integer, ForeignKey("notebooks.id"), nullable=True)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

    creator = relationship("User", back_populates="notebooks")
    compute_sessions = relationship("ComputeSession", back_populates="notebook")
    forks = relationship("Notebook", backref="parent", remote_side=[id])
    linked_datasets = relationship(
        "Dataset",
        secondary="dataset_notebook_links",
        back_populates="linked_notebooks",
    )


class ComputeSession(Base):
    __tablename__ = "compute_sessions"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    notebook_id = Column(Integer, ForeignKey("notebooks.id"), nullable=True)
    container_id = Column(String(100), nullable=True)
    hardware_target = Column(Enum(ComputeHardware), default=ComputeHardware.CPU)
    session_status = Column(Enum(SessionStatus), default=SessionStatus.ACTIVE)
    start_time = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    end_time = Column(DateTime(timezone=True), nullable=True)
    allowed_quota_remaining_minutes = Column(Integer, default=60 * 10)

    notebook = relationship("Notebook", back_populates="compute_sessions")
