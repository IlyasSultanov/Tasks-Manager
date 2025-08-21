from sqlalchemy import Column, Integer, String, Enum as SQLEnum, UUID, Text, DateTime
from db.base_class import BaseModel
from uuid import uuid4
from enum import Enum
from datetime import datetime, timezone


class TaskStatus(str, Enum):
    CREATED = "created"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"


class TaskModel(BaseModel):
    """Task model"""

    __tablename__ = "tasks"

    title = Column(String(200), nullable=False)
    description = Column(Text, nullable=False)
    status = Column(SQLEnum(TaskStatus), default=TaskStatus.CREATED)
