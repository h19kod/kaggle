from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.api.deps import get_current_active_user
from app.core.database import get_db
from app.core.s3_client import s3_service
from app.crud.dataset import dataset_crud, dataset_file_crud
from app.models.dataset import Dataset as DatasetModel
from app.models.user import User
from app.schemas.dataset import Dataset, DatasetCreate, DatasetUpdate, DatasetFile, DatasetFileCreate

router = APIRouter()


@router.get("/", response_model=List[Dataset])
def list_datasets(
    skip: int = 0,
    limit: int = 100,
    search: str = None,
    sort: str = "newest",
    db: Session = Depends(get_db),
):
    query = db.query(DatasetModel).filter(DatasetModel.is_public == True, DatasetModel.status == "Active")
    if search:
        query = query.filter(DatasetModel.title.ilike(f"%{search}%"))
    if sort == "newest":
        query = query.order_by(DatasetModel.created_at.desc())
    elif sort == "downloads":
        query = query.order_by(DatasetModel.downloads_count.desc())
    return query.offset(skip).limit(limit).all()


@router.post("/")
def create_dataset(
    dataset_in: DatasetCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    dataset_in.owner_id = current_user.id
    dataset = dataset_crud.create(db, obj_in=dataset_in)
    presigned_url = s3_service.generate_presigned_url(
        key=f"datasets/{dataset.id}/{dataset.slug}",
        expiration=900,
    )
    return {"dataset": dataset, "upload_url": presigned_url}


@router.get("/{dataset_id}", response_model=Dataset)
def read_dataset(dataset_id: int, db: Session = Depends(get_db)):
    dataset = dataset_crud.get(db, id=dataset_id)
    if not dataset:
        raise HTTPException(status_code=404, detail="Dataset not found")
    return dataset


@router.get("/slug/{slug}", response_model=Dataset)
def read_dataset_by_slug(slug: str, db: Session = Depends(get_db)):
    dataset = dataset_crud.get_by_slug(db, slug=slug)
    if not dataset:
        raise HTTPException(status_code=404, detail="Dataset not found")
    return dataset


@router.put("/{dataset_id}", response_model=Dataset)
def update_dataset(
    dataset_id: int,
    dataset_in: DatasetUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    dataset = dataset_crud.get(db, id=dataset_id)
    if not dataset:
        raise HTTPException(status_code=404, detail="Dataset not found")
    if dataset.owner_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized")
    return dataset_crud.update(db, db_obj=dataset, obj_in=dataset_in)


@router.delete("/{dataset_id}")
def delete_dataset(
    dataset_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    dataset = dataset_crud.get(db, id=dataset_id)
    if not dataset:
        raise HTTPException(status_code=404, detail="Dataset not found")
    if dataset.owner_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized")
    dataset_crud.remove(db, id=dataset_id)
    return {"message": "Dataset deleted"}


@router.get("/{dataset_id}/download")
def download_dataset(dataset_id: int, db: Session = Depends(get_db)):
    dataset = dataset_crud.get(db, id=dataset_id)
    if not dataset:
        raise HTTPException(status_code=404, detail="Dataset not found")
    if not dataset.is_public:
        raise HTTPException(status_code=403, detail="Dataset is private")
    dataset.downloads_count += 1
    db.add(dataset)
    db.commit()
    presigned_url = s3_service.generate_presigned_url(
        key=f"datasets/{dataset.id}/{dataset.slug}",
        expiration=3600,
    )
    return {"download_url": presigned_url}


@router.get("/{dataset_id}/files", response_model=List[DatasetFile])
def list_dataset_files(dataset_id: int, db: Session = Depends(get_db)):
    return dataset_file_crud.get_by_dataset(db, dataset_id=dataset_id)


@router.post("/{dataset_id}/files", response_model=DatasetFile)
def add_dataset_file(
    dataset_id: int,
    file_in: DatasetFileCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    dataset = dataset_crud.get(db, id=dataset_id)
    if not dataset:
        raise HTTPException(status_code=404, detail="Dataset not found")
    if dataset.owner_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized")
    file_in.dataset_id = dataset_id
    return dataset_file_crud.create(db, obj_in=file_in)
