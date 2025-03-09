from fastapi import FastAPI, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from contextlib import asynccontextmanager
from . import models, database
from typing import Optional


app = FastAPI()
@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan context manager to handle startup and shutdown"""
    # Startup
    print("Starting up, creating database tables...")
    models.Base.metadata.create_all(bind=database.engine)
    yield
    # Shutdown (optional, here just an example)
    print("Shutting down, closing database connection.")
    # Add any shutdown logic if needed, e.g. closing DB connection.
app = FastAPI(lifespan=lifespan)

@app.get("/")
def read_root():
    return {"message": "Hello, FastAPI!"}


@app.post("/tasks/", response_model=models.TaskResponse)
def create_task(task: models.TaskCreate, db: Session = Depends(database.get_db)):
    """
    Create a new task.

    This endpoint allows users to create a new task with a title, description, priority,
    due date, and completion status.

    **Request Body:**
    - `title`: The title of the task.
    - `description` (Optional): A detailed description of the task.
    - `priority`: Priority level of the task (1 = High, 5 = Low).
    - `due_date`: The due date for task completion (ISO 8601 format).
    - `completed`: Boolean flag indicating if the task is completed.

    **Responses:**
    - `201 Created`: Returns the newly created task.
    - `400 Bad Request`: If the input data is invalid.

    """
    db_task = models.Task(
        title=task.title,
        description=task.description,
        priority=task.priority.value,
        due_date=task.due_date,
        completed=task.completed
    )
    db.add(db_task)
    db.commit()
    db.refresh(db_task)
    return db_task


@app.get("/tasks/", response_model=list[models.TaskResponse])
def get_tasks(
    completed: Optional[bool] = Query(None, title="Completed Status", description="Filter by completion status (true or false)"),
    priority: Optional[int] = Query(None, gt=0, title="Priority Level", description="Filter tasks by priority (must be greater than 0)"),
    db: Session = Depends(database.get_db)
    ):
    """
    Retrieve all tasks.

    This endpoint returns a list of all tasks stored in the system.
    Optional filter queries include priority and completed status

    **Responses:**
    - `200 OK`: A list of tasks.
    - `204 No Content`: If no tasks are available.

    """
    query = db.query(models.Task)
    if completed is not None:
        query = query.filter(models.Task.completed == completed)

    if priority is not None:
        query = query.filter(models.Task.priority == priority)

    tasks = query.all()
    return tasks


@app.get("/tasks/{task_id}", response_model=models.TaskResponse)
def get_task(task_id: int, db: Session = Depends(database.get_db)):
    """
    Retrieve a task by ID.

    **Path Parameters:**
    - `task_id`: The unique identifier of the task.

    **Responses:**
    - `200 OK`: Returns the requested task.
    - `404 Not Found`: If the task does not exist.

    """
    task = db.query(models.Task).filter(models.Task.id == task_id).first()
    if task is None:
        raise HTTPException(status_code=404, detail="Task not found")
    return task


@app.put("/tasks/{task_id}", response_model=models.TaskResponse)
def update_task(task_id: int, task: models.TaskCreate, db: Session = Depends(database.get_db)):
    """
    Update an existing task.

    **Path Parameters:**
    - `task_id`: The unique identifier of the task to be updated.

    **Request Body:**
    - `id`: Unique identifier of the task.
    - `title`: The title of the task.
    - `description` (Optional): A detailed description of the task.
    - `priority`: Priority level of the task (1 = High, 5 = Low).
    - `due_date`: The due date for task completion (ISO 8601 format).
    - `completed`: Boolean flag indicating if the task is completed.

    **Responses:**
    - `200 OK`: Returns the updated task.
    - `404 Not Found`: If the task does not exist.

    """
    db_task = db.query(models.Task).filter(models.Task.id == task_id).first()
    if db_task is None:
        raise HTTPException(status_code=404, detail="Task not found")
    db_task.title = task.title
    db_task.description = task.description
    db_task.priority = task.priority.value
    db_task.due_date = task.due_date
    db_task.completed = task.completed
    db.commit()
    db.refresh(db_task)
    return db_task


@app.delete("/tasks/{task_id}", response_model=models.TaskResponse)
def delete_task(task_id: int, db: Session = Depends(database.get_db)):
    """
    Delete a task by ID.

    **Path Parameters:**
    - `task_id`: The unique identifier of the task to delete.

    **Responses:**
    - `200 OK`: Returns the deleted task.
    - `404 Not Found`: If the task does not exist.

    """
    db_task = db.query(models.Task).filter(models.Task.id == task_id).first()
    if db_task is None:
        raise HTTPException(status_code=404, detail="Task not found")
    db.delete(db_task)
    db.commit()
    return db_task
