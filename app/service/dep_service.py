from fastapi import Depends
from db.session import AsyncSession, get_db
from service.service import TaskService


def get_task_service(db: AsyncSession = Depends(get_db)):
    return TaskService(db)

