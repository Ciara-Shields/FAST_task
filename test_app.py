import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.models import Base, Task  # Import your models
from fastapi.testclient import TestClient
from app.main import app  # Your FastAPI app
from datetime import datetime

# In-memory SQLite database for testing
SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"

# Create engine and session
engine = create_engine(SQLALCHEMY_DATABASE_URL, echo=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create tables in the in-memory database
Base.metadata.create_all(bind=engine)

# Test Client fixture
@pytest.fixture(scope="module")
def test_client():
    client = TestClient(app)
    yield client
    # Cleanup after tests (optional, if you want to drop tables after tests)
    Base.metadata.drop_all(bind=engine)

# Session fixture for each test function
@pytest.fixture(scope="function")
def db_session():
    db = SessionLocal()  # Create a new session for each test
    try:
        yield db  # Provide the session to the test function
    finally:
        db.close()  # Close the session after the test

# Mock data fixture (can be reused in multiple tests)
@pytest.fixture
def mock_task():
    task = Task(
        title="Test Task",
        description="Test Description",
        priority=1,
        due_date=datetime(2025, 5, 10, 10, 0, 0),
        completed=False,
    )
    return task



def test_create_task(test_client, db_session, mock_task):
    # Add task to the database
    db_session.add(mock_task)
    db_session.commit()

    # Send POST request to create task via API
    response = test_client.post("/tasks/", json={
        "title": "Get Milk",
        "description": "Get Milk",
        "priority": 2,
        "due_date": "2025-03-10T10:00:00",  # Send the due date as a string (FastAPI will convert it to a datetime)
        "completed": False
    })

    # Assert the response status code is 201 (created)
    assert response.status_code == 200

    # Assert the task was actually created in the response
    task_from_response = response.json()
    assert task_from_response["title"] == "Get Milk"
    assert task_from_response["description"] == "Get Milk"
    assert task_from_response["priority"] == 2
    assert task_from_response["due_date"] == "2025-03-10T10:00:00"  # Ensure the response matches the input
    assert task_from_response["completed"] == False


