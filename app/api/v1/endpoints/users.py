from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.api.deps import get_current_active_user
from app.core.database import get_db
from app.crud.user import user_crud, profile_crud
from app.models.user import User
from app.schemas.user import UserUpdate, UserProfile, UserProfileUpdate

router = APIRouter()


@router.get("/me")
def read_user_me(current_user: User = Depends(get_current_active_user)):
    return current_user


@router.put("/me")
def update_user_me(
    user_in: UserUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    return user_crud.update(db, db_obj=current_user, obj_in=user_in)


@router.get("/{username}")
def read_user_public(username: str, db: Session = Depends(get_db)):
    user = user_crud.get_by_username(db, username=username)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    profile = profile_crud.get_by_user(db, user_id=user.id)
    return {
        "id": user.id,
        "username": user.username,
        "global_tier": user.global_tier.value if user.global_tier else None,
        "created_at": user.created_at,
        "profile": profile,
    }


@router.put("/profile/update", response_model=UserProfile)
def update_my_profile(
    profile_in: UserProfileUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    profile = profile_crud.get_by_user(db, user_id=current_user.id)
    if not profile:
        raise HTTPException(status_code=404, detail="Profile not found")
    return profile_crud.update(db, db_obj=profile, obj_in=profile_in)
