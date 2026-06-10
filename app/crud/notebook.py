from typing import List, Optional
from sqlalchemy.orm import Session
from app.crud.base import CRUDBase
from app.models.notebook import Notebook, ComputeSession
from app.schemas.notebook import NotebookCreate, NotebookUpdate, ComputeSessionCreate


class CRUDNotebook(CRUDBase[Notebook, NotebookCreate, NotebookUpdate]):
    def get_by_creator(self, db: Session, *, creator_id: int, skip: int = 0, limit: int = 100) -> List[Notebook]:
        return (
            db.query(Notebook)
            .filter(Notebook.creator_id == creator_id)
            .offset(skip)
            .limit(limit)
            .all()
        )

    def get_forks(self, db: Session, *, notebook_id: int) -> List[Notebook]:
        return db.query(Notebook).filter(Notebook.forked_from_id == notebook_id).all()


class CRUDComputeSession(CRUDBase[ComputeSession, ComputeSessionCreate, ComputeSessionCreate]):
    def get_active_by_user(self, db: Session, *, user_id: int) -> List[ComputeSession]:
        return (
            db.query(ComputeSession)
            .filter(ComputeSession.user_id == user_id, ComputeSession.session_status == "Active")
            .all()
        )

    def get_by_notebook(self, db: Session, *, notebook_id: int) -> List[ComputeSession]:
        return db.query(ComputeSession).filter(ComputeSession.notebook_id == notebook_id).all()


notebook_crud = CRUDNotebook(Notebook)
compute_session_crud = CRUDComputeSession(ComputeSession)
