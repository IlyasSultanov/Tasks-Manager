from fastapi import Depends, HTTPException
from uuid import UUID
from schemas import schemas
from models import models
from db.session import AsyncSession
from sqlalchemy import select, and_


class TaskService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_task(self, task: schemas.TaskCreate):
        db_task = models.TaskModel(title=task.title, description=task.description)
        self.db.add(db_task)
        await self.db.commit()
        await self.db.refresh(db_task)
        return db_task

    async def get_tasks(self, skip: int = 0, limit: int = 100):
        query = select(models.TaskModel).offset(skip).limit(limit)
        tasks = await self.db.execute(query)
        tasks = tasks.scalars().all()
        return tasks

    async def get_task(self, task_id: UUID):
        query = select(models.TaskModel).where(and_(models.TaskModel.id == task_id))
        task = await self.db.execute(query)
        task = task.scalar_one_or_none()
        if not task:
            raise HTTPException(status_code=404, detail="Task not found")
        return task

    async def update_task(self, task_id: UUID, task_update: schemas.TaskUpdate):
        query = select(models.TaskModel).where(and_(models.TaskModel.id == task_id))
        task = await self.db.execute(query)
        task = task.scalar_one_or_none()
        if not task:
            raise HTTPException(status_code=404, detail="Task not found")

        update_data = task_update.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(task, key, value)

        await self.db.commit()
        await self.db.refresh(task)
        return task

    async def delete_task(self, task_id: UUID):
        query = select(models.TaskModel).where(models.TaskModel.id == task_id)
        task = await self.db.execute(query)
        task = task.scalar_one_or_none()
        if not task:
            raise HTTPException(status_code=404, detail="Task not found")
        await self.db.delete(task)
        await self.db.commit()
        return None
