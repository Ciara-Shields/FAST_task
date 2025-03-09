Task tracker made wit Fast API

This API can be used to create, update, retrieve and delete tasks
The tasks model schema is:
    - id (int): Primary key.
    - title (string): Task title (required).
    - description (string): Task description (optional).
    - priority (int): Task priority (1 = High, 2 = Medium, 3 = Low).
    - due_date (datetime): Due date for the task.
    - completed (bool): Completion status (default: False).

To run locally:
create virtual environment -> python3 -m venv taskvenv
run app in Docker -> docker-compose up --build

To run tests : 
command to run tests -> pytest


Example API calls:
FAST UI can be found at http://0.0.0.0:8010/docs

GET : curl -X GET http://0.0.0.0:8010/tasks/{id}
POST: curl -X POST "http://0.0.0.0:8010/tasks/" \
     -H "Content-Type: application/json" \
     -d '{
           "title": "My New Task",
           "description": "This is a test task",
           "priority": 2,
           "due_date": "2025-03-08T10:00:00",
         }'
PUT: curl -X PUT "http://0.0.0.0:8010/tasks/{id}" \
     -H "Content-Type: application/json" \
     -d '{
           "completed": true, #updated field
         }'
DELETE: curl -X DELETE http://0.0.0.0:8010/tasks/{id}
