from typing import List, Optional
from sqlalchemy.orm import Session
from app.crud.base import CRUDBase
from app.models.community import DiscussionPost, Upvote
from app.schemas.community import DiscussionPostCreate, DiscussionPostUpdate, UpvoteCreate


class CRUDDiscussionPost(CRUDBase[DiscussionPost, DiscussionPostCreate, DiscussionPostUpdate]):
    def get_by_category(self, db: Session, *, category: str, skip: int = 0, limit: int = 100) -> List[DiscussionPost]:
        return (
            db.query(DiscussionPost)
            .filter(DiscussionPost.category == category)
            .offset(skip)
            .limit(limit)
            .all()
        )

    def get_by_author(self, db: Session, *, author_id: int, skip: int = 0, limit: int = 100) -> List[DiscussionPost]:
        return (
            db.query(DiscussionPost)
            .filter(DiscussionPost.author_id == author_id)
            .offset(skip)
            .limit(limit)
            .all()
        )


class CRUDUpvote(CRUDBase[Upvote, UpvoteCreate, UpvoteCreate]):
    def get_by_user_and_target(self, db: Session, *, user_id: int, target_type: str, target_id: int) -> Optional[Upvote]:
        return (
            db.query(Upvote)
            .filter(Upvote.user_id == user_id, Upvote.target_type == target_type, Upvote.target_id == target_id)
            .first()
        )

    def count_by_target(self, db: Session, *, target_type: str, target_id: int) -> int:
        return (
            db.query(Upvote)
            .filter(Upvote.target_type == target_type, Upvote.target_id == target_id)
            .count()
        )


discussion_post_crud = CRUDDiscussionPost(DiscussionPost)
upvote_crud = CRUDUpvote(Upvote)
