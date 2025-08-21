from fastapi import APIRouter
from router import router as tasks_router

router = APIRouter(prefix="/tasks", tags=["TASKS"])

router.include_router(tasks_router)