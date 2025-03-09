import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.models import Base, Task
from app.database import get_db
from fastapi.testclient import TestClient
from app.main import app
from datetime import datetime

# Create a test engine (in-memory)
SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"
engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


# --- Create Tables ---
@pytest.fixture(scope="session", autouse=True)
def create_test_db():
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


# --- Session Fixture ---
@pytest.fixture(scope="function")
def db_session():
    connection = engine.connect()
    transaction = connection.begin()
    session = TestingSessionLocal(bind=connection)
    yield session
    session.close()
    transaction.rollback()
    connection.close()


# --- Override Dependency ---
@pytest.fixture(scope="function")
def test_client(db_session):
    def override_get_db():
        try:
            yield db_session
        finally:
            pass

    app.dependency_overrides[get_db] = override_get_db
    client = TestClient(app)
    yield client
    app.dependency_overrides.clear()  # Clean up overrides after test

@pytest.fixture
def mock_task():
    task = Task(
        title="Test Task",
        description="Test Description",
        priority=1,
        due_date=datetime(2025, 5, 10, 10, 0, 0),
        completed=False,
        id=1
    )
    return task


def test_create_task(test_client, db_session):
    response = test_client.post("/tasks/", json={
        "title": "Get Tea",
        "description": "Get Tea",
        "priority": 2,
        "due_date": "2025-03-10T10:00:00",
    })
    db_session.commit()
    assert response.status_code == 200
    task_from_response = response.json()
    assert task_from_response["title"] == "Get Tea"
    assert task_from_response["description"] == "Get Tea"
    assert task_from_response["priority"] == 2
    assert task_from_response["due_date"] == "2025-03-10T10:00:00"
    assert task_from_response["completed"] == False


def test_create_task_missing_data(test_client, db_session):
    response = test_client.post("/tasks/", json={
        "title": "Get Milk",
        "due_date": "2025-03-10T10:00:00"
    })
    db_session.commit()
    assert response.status_code == 422
    
def test_create_task_invalid_data_type (test_client, db_session):
    response = test_client.post("/tasks/", json={
        "title": "Get Milk",
        "priority": 'HIGH',
        "due_date": "2025-03-10T10:00:00",
    })
    db_session.commit()
    assert response.status_code == 422
    
def test_delete_task(test_client, db_session, mock_task):
    db_session.add(mock_task)
    db_session.commit()
    task_in_db = db_session.query(Task).filter(Task.title == "Test Task").first()
    response = test_client.delete(f"/tasks/{task_in_db.id}")
    assert response.status_code == 200
    assert response.json() == {
        "message": f"Task '{task_in_db.title}' with ID {task_in_db.id} deleted successfully."
    }
    
    # Send DELETE request again (expecting a 404 error as the task does not exist)
    response = test_client.delete(f"/tasks/{task_in_db.id}")
    assert response.status_code == 404
    assert response.json() == {"detail": "Task not found"}