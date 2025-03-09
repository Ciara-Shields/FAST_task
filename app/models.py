from pydantic import BaseModel
from sqlalchemy import Column, Integer, String, Boolean, DateTime, Enum
from sqlalchemy.ext.declarative import declarative_base
import datetime
from sqlalchemy.sql import func
from typing import Optional
from enum import Enum as PyEnum
from app.database import Base

# Base = declarative_base()
class Priority(PyEnum):
    HIGH = 1
    MED = 2
    LOW = 3
class Task(Base):
    __tablename__ = 'tasks'

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True)
    description = Column(String, nullable=True)
    priority = Column(Integer, nullable=False)
    due_date = Column(DateTime, default=func.now())  # Updated to use func.now() instead of datetime.utcnow
    completed = Column(Boolean, default=False)

# Pydantic model (for request validation - Task creation)
class TaskCreate(BaseModel):
    title: str
    description: Optional[str] = None  # description is optional
    priority: Priority
    due_date: datetime.datetime
    completed: bool = False

    class Config:
        orm_mode = True  # Tells Pydantic to treat SQLAlchemy models as dictionaries

# Pydantic model for response (Task with 'id')
class TaskResponse(TaskCreate):
    id: int  # We include the 'id' field for response model

class TaskUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    priority: Optional[int] = None
    due_date: Optional[datetime.datetime] = None
    completed: Optional[bool] = None
