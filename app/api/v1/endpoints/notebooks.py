from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.api.deps import get_current_active_user
from app.core.config import settings
from app.core.database import get_db
from app.tasks.compute import start_compute_session as start_compute_session_task
from app.crud.notebook import notebook_crud, compute_session_crud
from app.models.user import User
from app.schemas.notebook import Notebook, NotebookCreate, NotebookUpdate, ComputeSession, ComputeSessionCreate

router = APIRouter()


@router.get("/", response_model=List[Notebook])
def list_notebooks(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return notebook_crud.get_multi(db, skip=skip, limit=limit)


@router.post("/", response_model=Notebook)
def create_notebook(
    notebook_in: NotebookCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    notebook_in.creator_id = current_user.id
    return notebook_crud.create(db, obj_in=notebook_in)


@router.get("/{notebook_id}", response_model=Notebook)
def read_notebook(notebook_id: int, db: Session = Depends(get_db)):
    notebook = notebook_crud.get(db, id=notebook_id)
    if not notebook:
        raise HTTPException(status_code=404, detail="Notebook not found")
    return notebook


@router.put("/{notebook_id}", response_model=Notebook)
def update_notebook(
    notebook_id: int,
    notebook_in: NotebookUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    notebook = notebook_crud.get(db, id=notebook_id)
    if not notebook:
        raise HTTPException(status_code=404, detail="Notebook not found")
    if notebook.creator_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized")
    return notebook_crud.update(db, db_obj=notebook, obj_in=notebook_in)


@router.delete("/{notebook_id}")
def delete_notebook(
    notebook_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    notebook = notebook_crud.get(db, id=notebook_id)
    if not notebook:
        raise HTTPException(status_code=404, detail="Notebook not found")
    if notebook.creator_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized")
    notebook_crud.remove(db, id=notebook_id)
    return {"message": "Notebook deleted"}


@router.post("/{notebook_id}/fork", response_model=Notebook)
def fork_notebook(
    notebook_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    original = notebook_crud.get(db, id=notebook_id)
    if not original:
        raise HTTPException(status_code=404, detail="Notebook not found")
    fork_data = NotebookCreate(
        title=f"Fork of {original.title}",
        description=original.description,
        language=original.language,
        storage_path_url=original.storage_path_url,
        creator_id=current_user.id,
        forked_from_id=original.id,
    )
    return notebook_crud.create(db, obj_in=fork_data)


@router.post("/{notebook_id}/attach-dataset")
def attach_dataset(
    notebook_id: int,
    dataset_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    from app.models.dataset import dataset_notebook_links
    from app.crud.dataset import dataset_crud
    notebook = notebook_crud.get(db, id=notebook_id)
    if not notebook:
        raise HTTPException(status_code=404, detail="Notebook not found")
    dataset = dataset_crud.get(db, id=dataset_id)
    if not dataset:
        raise HTTPException(status_code=404, detail="Dataset not found")
    stmt = dataset_notebook_links.insert().values(notebook_id=notebook_id, dataset_id=dataset_id)
    db.execute(stmt)
    db.commit()
    return {"message": "Dataset attached to notebook"}


@router.post("/{notebook_id}/session/start")
def start_compute_session(
    notebook_id: int,
    session_in: ComputeSessionCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    notebook = notebook_crud.get(db, id=notebook_id)
    if not notebook:
        raise HTTPException(status_code=404, detail="Notebook not found")
    if notebook.creator_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized")
    session_in.notebook_id = notebook_id
    session_in.user_id = current_user.id
    db_session = compute_session_crud.create(db, obj_in=session_in)

    dataset_mounts = []
    for ds in notebook.linked_datasets:
        for f in ds.files:
            dataset_mounts.append({
                "host_path": f.storage_path_url.replace(f"{settings.S3_ENDPOINT}/{settings.S3_BUCKET_NAME}/", ""),
                "container_path": f"/kaggle/input/{ds.slug}/{f.file_name}",
            })

    task = start_compute_session_task.delay(
        session_id=db_session.id,
        hardware=session_in.hardware_target,
        dataset_mounts=dataset_mounts,
    )
    return {"session": db_session, "task_id": task.id}
