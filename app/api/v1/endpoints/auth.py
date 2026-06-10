from datetime import timedelta
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.config import settings
from app.core.security import create_access_token
from app.crud.user import user_crud, profile_crud
from app.schemas.user import UserCreate, User, UserProfileCreate

router = APIRouter()


@router.post("/register", response_model=User)
def register(user_in: UserCreate, db: Session = Depends(get_db)):
    user = user_crud.get_by_email(db, email=user_in.email)
    if user:
        raise HTTPException(status_code=400, detail="Email already registered")
    user = user_crud.get_by_username(db, username=user_in.username)
    if user:
        raise HTTPException(status_code=400, detail="Username already taken")
    user = user_crud.create(db, obj_in=user_in)
    profile_in = UserProfileCreate(user_id=user.id)
    profile_crud.create(db, obj_in=profile_in)
    return user


@router.post("/login")
def login(db: Session = Depends(get_db), form_data: OAuth2PasswordRequestForm = Depends()):
    user = user_crud.authenticate(db, username=form_data.username, password=form_data.password)
    if not user:
        raise HTTPException(status_code=400, detail="Incorrect username or password")
    access_token = create_access_token(subject=user.id)
    return {"access_token": access_token, "token_type": "bearer"}
