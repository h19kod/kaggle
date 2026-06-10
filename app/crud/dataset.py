from typing import List, Optional
from sqlalchemy.orm import Session
from app.crud.base import CRUDBase
from app.models.dataset import Dataset, DatasetFile
from app.schemas.dataset import DatasetCreate, DatasetUpdate, DatasetFileCreate


class CRUDDataset(CRUDBase[Dataset, DatasetCreate, DatasetUpdate]):
    def get_by_slug(self, db: Session, *, slug: str) -> Optional[Dataset]:
        return db.query(Dataset).filter(Dataset.slug == slug).first()

    def get_by_owner(self, db: Session, *, owner_id: int, skip: int = 0, limit: int = 100) -> List[Dataset]:
        return (
            db.query(Dataset)
            .filter(Dataset.owner_id == owner_id)
            .offset(skip)
            .limit(limit)
            .all()
        )

    def get_public(self, db: Session, *, skip: int = 0, limit: int = 100) -> List[Dataset]:
        return (
            db.query(Dataset)
            .filter(Dataset.is_public == True)
            .offset(skip)
            .limit(limit)
            .all()
        )


class CRUDDatasetFile(CRUDBase[DatasetFile, DatasetFileCreate, DatasetFileCreate]):
    def get_by_dataset(self, db: Session, *, dataset_id: int) -> List[DatasetFile]:
        return db.query(DatasetFile).filter(DatasetFile.dataset_id == dataset_id).all()


dataset_crud = CRUDDataset(Dataset)
dataset_file_crud = CRUDDatasetFile(DatasetFile)
