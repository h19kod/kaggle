from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.api.deps import get_current_active_user
from app.core.database import get_db
from app.core.redis_client import cache
from app.crud.community import discussion_post_crud, upvote_crud
from app.crud.user import profile_crud
from app.crud.dataset import dataset_crud
from app.crud.notebook import notebook_crud
from app.models.user import User, UserTier
from app.schemas.community import DiscussionPost, DiscussionPostCreate, DiscussionPostUpdate, Upvote, UpvoteCreate

posts_router = APIRouter()
upvote_router = APIRouter()


TIER_THRESHOLDS = {
    UserTier.CONTRIBUTOR: 10,
    UserTier.EXPERT: 50,
    UserTier.MASTER: 100,
    UserTier.GRANDMASTER: 500,
}


def _get_target_owner(db: Session, target_type: str, target_id: int):
    if target_type == "Dataset":
        obj = dataset_crud.get(db, id=target_id)
        return obj.owner_id if obj else None
    elif target_type == "Notebook":
        obj = notebook_crud.get(db, id=target_id)
        return obj.creator_id if obj else None
    elif target_type == "Post":
        obj = discussion_post_crud.get(db, id=target_id)
        return obj.author_id if obj else None
    return None


def _evaluate_tier(total_upvotes: int) -> UserTier:
    if total_upvotes >= TIER_THRESHOLDS[UserTier.GRANDMASTER]:
        return UserTier.GRANDMASTER
    if total_upvotes >= TIER_THRESHOLDS[UserTier.MASTER]:
        return UserTier.MASTER
    if total_upvotes >= TIER_THRESHOLDS[UserTier.EXPERT]:
        return UserTier.EXPERT
    if total_upvotes >= TIER_THRESHOLDS[UserTier.CONTRIBUTOR]:
        return UserTier.CONTRIBUTOR
    return UserTier.NOVICE


@posts_router.get("/", response_model=List[DiscussionPost])
def list_posts(skip: int = 0, limit: int = 100, category: str = None, db: Session = Depends(get_db)):
    if category:
        return discussion_post_crud.get_by_category(db, category=category, skip=skip, limit=limit)
    return discussion_post_crud.get_multi(db, skip=skip, limit=limit)


@posts_router.post("/", response_model=DiscussionPost)
def create_post(
    post_in: DiscussionPostCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    post_in.author_id = current_user.id
    return discussion_post_crud.create(db, obj_in=post_in)


@posts_router.get("/{post_id}", response_model=DiscussionPost)
def read_post(post_id: int, db: Session = Depends(get_db)):
    post = discussion_post_crud.get(db, id=post_id)
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
    return post


@posts_router.put("/{post_id}", response_model=DiscussionPost)
def update_post(
    post_id: int,
    post_in: DiscussionPostUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    post = discussion_post_crud.get(db, id=post_id)
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
    if post.author_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized")
    return discussion_post_crud.update(db, db_obj=post, obj_in=post_in)


@posts_router.delete("/{post_id}")
def delete_post(
    post_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    post = discussion_post_crud.get(db, id=post_id)
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
    if post.author_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized")
    discussion_post_crud.remove(db, id=post_id)
    return {"message": "Post deleted"}


@upvote_router.post("/")
def create_upvote(
    upvote_in: UpvoteCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    existing = upvote_crud.get_by_user_and_target(
        db,
        user_id=current_user.id,
        target_type=upvote_in.target_type,
        target_id=upvote_in.target_id,
    )
    if existing:
        raise HTTPException(status_code=400, detail="Already upvoted")
    upvote_in.user_id = current_user.id
    upvote = upvote_crud.create(db, obj_in=upvote_in)

    # Progression logic
    owner_id = _get_target_owner(db, upvote_in.target_type, upvote_in.target_id)
    if owner_id:
        total = upvote_crud.count_by_target(db, target_type=upvote_in.target_type, target_id=upvote_in.target_id)
        profile = profile_crud.get_by_user(db, user_id=owner_id)
        if profile:
            profile.total_upvotes = total
            db.add(profile)
            db.commit()

            new_tier = _evaluate_tier(total)
            from app.crud.user import user_crud
            owner = user_crud.get(db, id=owner_id)
            if owner and owner.global_tier != new_tier:
                old_tier = owner.global_tier.value if owner.global_tier else "Novice"
                owner.global_tier = new_tier
                db.add(owner)
                db.commit()
                cache.publish(
                    f"notifications:{owner_id}",
                    {
                        "event": "tier_upgraded",
                        "user_id": owner_id,
                        "old_tier": old_tier,
                        "new_tier": new_tier.value,
                        "reason": f"Reached {total} upvotes",
                    }
                )

    return upvote
