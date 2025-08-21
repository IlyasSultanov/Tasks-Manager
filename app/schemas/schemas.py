from uuid import UUID
from enum import Enum
from pydantic import BaseModel

"""
Schemas for the Task model
"""


class TaskStatus(str, Enum):
    CREATED = "created"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"


class TaskBase(BaseModel):
    title: str
    description: str


class TaskCreate(TaskBase):
    pass


class TaskUpdate(BaseModel):
    title: str | None = None
    description: str | None = None
    status: TaskStatus | None = None


class Task(TaskBase):
    id: UUID
    status: TaskStatus

    class Config:
        from_attributes = True  
