from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from contextlib import asynccontextmanager
from . import models, database

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

# Create a new task
@app.post("/tasks/", response_model=models.TaskResponse)
def create_task(task: models.TaskCreate, db: Session = Depends(database.get_db)):
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

# Get a list of tasks
@app.get("/tasks/", response_model=list[models.TaskResponse])
def read_tasks(db: Session = Depends(database.get_db)):
    tasks = db.query(models.Task).all()
    return tasks

# Get a task by ID
@app.get("/tasks/{task_id}", response_model=models.TaskResponse)
def read_task(task_id: int, db: Session = Depends(database.get_db)):
    task = db.query(models.Task).filter(models.Task.id == task_id).first()
    if task is None:
        raise HTTPException(status_code=404, detail="Task not found")
    return task

# Update a task
@app.put("/tasks/{task_id}", response_model=models.TaskResponse)
def update_task(task_id: int, task: models.TaskCreate, db: Session = Depends(database.get_db)):
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

# Delete a task
@app.delete("/tasks/{task_id}", response_model=models.TaskResponse)
def delete_task(task_id: int, db: Session = Depends(database.get_db)):
    db_task = db.query(models.Task).filter(models.Task.id == task_id).first()
    if db_task is None:
        raise HTTPException(status_code=404, detail="Task not found")
    db.delete(db_task)
    db.commit()
    return db_task  # Returning the deleted task (SQLAlchemy model)
