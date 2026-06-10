from fastapi import APIRouter
from app.api.v1.endpoints import auth, users, datasets, notebooks, competitions, courses, community, jobs, ws

api_router = APIRouter()

api_router.include_router(auth.router, prefix="/auth", tags=["authentication"])
api_router.include_router(users.router, prefix="/users", tags=["users"])
api_router.include_router(datasets.router, prefix="/datasets", tags=["datasets"])
api_router.include_router(notebooks.router, prefix="/notebooks", tags=["notebooks"])
api_router.include_router(competitions.router, prefix="/competitions", tags=["competitions"])
api_router.include_router(courses.router, prefix="/courses", tags=["courses"])
api_router.include_router(courses.lessons_router, prefix="/lessons", tags=["lessons"])
api_router.include_router(community.posts_router, prefix="/posts", tags=["posts"])
api_router.include_router(community.upvote_router, prefix="/upvote", tags=["upvotes"])
api_router.include_router(jobs.router, prefix="/jobs", tags=["jobs"])
api_router.include_router(ws.router, prefix="/ws", tags=["websockets"])
