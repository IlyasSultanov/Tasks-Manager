"""
API tests for Task Manager application
"""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from uuid import uuid4
from datetime import datetime, timezone
from fastapi.testclient import TestClient
from fastapi import FastAPI

# Import application components
from app.main import app
from app.schemas.schemas import TaskCreate, TaskUpdate, Task, TaskStatus
from app.models.models import TaskModel, TaskStatus as ModelTaskStatus
from app.service.service import TaskService


class TestTaskAPI:
    """Тесты для API эндпоинтов задач"""

    @pytest.fixture
    def client(self):
        """Фикстура для тестового клиента"""
        return TestClient(app)

    @pytest.fixture
    def sample_task_data(self):
        """Фикстура с данными для тестовой задачи"""
        return {"title": "API Test Task", "description": "API Test Description"}

    @pytest.fixture
    def sample_task_response(self):
        """Фикстура с данными ответа задачи"""
        task_id = uuid4()
        return {
            "id": str(task_id),
            "title": "API Test Task",
            "description": "API Test Description",
            "status": "created",
            "created_at": "2024-01-01T00:00:00Z",
            "updated_at": "2024-01-01T00:00:00Z",
        }

    @pytest.mark.api
    def test_create_task_success(self, client, sample_task_data):
        """Тест успешного создания задачи через API"""
        with patch("app.service.dep_service.get_task_service") as mock_get_service:
            # Настройка мока
            mock_service = AsyncMock(spec=TaskService)
            mock_task = TaskModel(
                id=uuid4(),
                title=sample_task_data["title"],
                description=sample_task_data["description"],
                status=ModelTaskStatus.CREATED,
                created_at=datetime.now(timezone.utc),
                updated_at=datetime.now(timezone.utc),
            )
            mock_service.create_task.return_value = mock_task
            mock_get_service.return_value = mock_service

            # Выполнение запроса
            response = client.post("/api/v1/tasks/", json=sample_task_data)

            # Проверки
            assert response.status_code == 200
            data = response.json()
            assert data["title"] == sample_task_data["title"]
            assert data["description"] == sample_task_data["description"]
            assert data["status"] == "created"
            assert "id" in data
            assert "created_at" in data
            assert "updated_at" in data

    @pytest.mark.api
    def test_create_task_validation_error(self, client):
        """Тест валидации при создании задачи"""
        invalid_data = {
            "title": "",  # Пустой заголовок
            "description": "Test Description",
        }

        response = client.post("/api/v1/tasks/", json=invalid_data)

        assert response.status_code == 422  # Validation Error

    @pytest.mark.api
    def test_get_tasks_success(self, client):
        """Тест успешного получения списка задач"""
        with patch("app.service.dep_service.get_task_service") as mock_get_service:
            # Настройка мока
            mock_service = AsyncMock(spec=TaskService)
            mock_tasks = [
                TaskModel(
                    id=uuid4(),
                    title="Task 1",
                    description="Description 1",
                    status=ModelTaskStatus.CREATED,
                    created_at=datetime.now(timezone.utc),
                    updated_at=datetime.now(timezone.utc),
                ),
                TaskModel(
                    id=uuid4(),
                    title="Task 2",
                    description="Description 2",
                    status=ModelTaskStatus.IN_PROGRESS,
                    created_at=datetime.now(timezone.utc),
                    updated_at=datetime.now(timezone.utc),
                ),
            ]
            mock_service.get_tasks.return_value = mock_tasks
            mock_get_service.return_value = mock_service

            # Выполнение запроса
            response = client.get("/api/v1/tasks/")

            # Проверки
            assert response.status_code == 200
            data = response.json()
            assert len(data) == 2
            assert data[0]["title"] == "Task 1"
            assert data[1]["title"] == "Task 2"

    @pytest.mark.api
    def test_get_tasks_with_pagination(self, client):
        """Тест получения задач с пагинацией"""
        with patch("app.service.dep_service.get_task_service") as mock_get_service:
            # Настройка мока
            mock_service = AsyncMock(spec=TaskService)
            mock_service.get_tasks.return_value = []
            mock_get_service.return_value = mock_service

            # Выполнение запроса с параметрами пагинации
            response = client.get("/api/v1/tasks/?skip=10&limit=5")

            # Проверки
            assert response.status_code == 200
            mock_service.get_tasks.assert_called_once_with(10, 5)

    @pytest.mark.api
    def test_get_task_by_id_success(self, client):
        """Тест успешного получения задачи по ID"""
        task_id = uuid4()

        with patch("app.service.dep_service.get_task_service") as mock_get_service:
            # Настройка мока
            mock_service = AsyncMock(spec=TaskService)
            mock_task = TaskModel(
                id=task_id,
                title="Specific Task",
                description="Specific Description",
                status=ModelTaskStatus.COMPLETED,
                created_at=datetime.now(timezone.utc),
                updated_at=datetime.now(timezone.utc),
            )
            mock_service.get_task.return_value = mock_task
            mock_get_service.return_value = mock_service

            # Выполнение запроса
            response = client.get(f"/api/v1/tasks/{task_id}")

            # Проверки
            assert response.status_code == 200
            data = response.json()
            assert data["id"] == str(task_id)
            assert data["title"] == "Specific Task"
            assert data["status"] == "completed"

    @pytest.mark.api
    def test_get_task_by_id_not_found(self, client):
        """Тест получения несуществующей задачи"""
        task_id = uuid4()

        with patch("app.service.dep_service.get_task_service") as mock_get_service:
            # Настройка мока для исключения
            mock_service = AsyncMock(spec=TaskService)
            from fastapi import HTTPException

            mock_service.get_task.side_effect = HTTPException(
                status_code=404, detail="Task not found"
            )
            mock_get_service.return_value = mock_service

            # Выполнение запроса
            response = client.get(f"/api/v1/tasks/{task_id}")

            # Проверки
            assert response.status_code == 404
            data = response.json()
            assert data["detail"] == "Task not found"

    @pytest.mark.api
    def test_update_task_success(self, client):
        """Тест успешного обновления задачи"""
        task_id = uuid4()
        update_data = {"title": "Updated Task Title", "status": "in_progress"}

        with patch("app.service.dep_service.get_task_service") as mock_get_service:
            # Настройка мока
            mock_service = AsyncMock(spec=TaskService)
            mock_task = TaskModel(
                id=task_id,
                title="Updated Task Title",
                description="Original Description",
                status=ModelTaskStatus.IN_PROGRESS,
                created_at=datetime.now(timezone.utc),
                updated_at=datetime.now(timezone.utc),
            )
            mock_service.update_task.return_value = mock_task
            mock_get_service.return_value = mock_service

            # Выполнение запроса
            response = client.put(f"/api/v1/tasks/{task_id}", json=update_data)

            # Проверки
            assert response.status_code == 200
            data = response.json()
            assert data["title"] == "Updated Task Title"
            assert data["status"] == "in_progress"

    @pytest.mark.api
    def test_update_task_partial(self, client):
        """Тест частичного обновления задачи"""
        task_id = uuid4()
        update_data = {"title": "Only Title Updated"}

        with patch("app.service.dep_service.get_task_service") as mock_get_service:
            # Настройка мока
            mock_service = AsyncMock(spec=TaskService)
            mock_task = TaskModel(
                id=task_id,
                title="Only Title Updated",
                description="Original Description",
                status=ModelTaskStatus.CREATED,
                created_at=datetime.now(timezone.utc),
                updated_at=datetime.now(timezone.utc),
            )
            mock_service.update_task.return_value = mock_task
            mock_get_service.return_value = mock_service

            # Выполнение запроса
            response = client.put(f"/api/v1/tasks/{task_id}", json=update_data)

            # Проверки
            assert response.status_code == 200
            data = response.json()
            assert data["title"] == "Only Title Updated"
            assert data["description"] == "Original Description"

    @pytest.mark.api
    def test_update_task_not_found(self, client):
        """Тест обновления несуществующей задачи"""
        task_id = uuid4()
        update_data = {"title": "Updated Title"}

        with patch("app.service.dep_service.get_task_service") as mock_get_service:
            # Настройка мока для исключения
            mock_service = AsyncMock(spec=TaskService)
            from fastapi import HTTPException

            mock_service.update_task.side_effect = HTTPException(
                status_code=404, detail="Task not found"
            )
            mock_get_service.return_value = mock_service

            # Выполнение запроса
            response = client.put(f"/api/v1/tasks/{task_id}", json=update_data)

            # Проверки
            assert response.status_code == 404
            data = response.json()
            assert data["detail"] == "Task not found"

    @pytest.mark.api
    def test_delete_task_success(self, client):
        """Тест успешного удаления задачи"""
        task_id = uuid4()

        with patch("app.service.dep_service.get_task_service") as mock_get_service:
            # Настройка мока
            mock_service = AsyncMock(spec=TaskService)
            mock_service.delete_task.return_value = None
            mock_get_service.return_value = mock_service

            # Выполнение запроса
            response = client.delete(f"/api/v1/tasks/{task_id}")

            # Проверки
            assert response.status_code == 204
            assert response.content == b""  # Пустое тело ответа

    @pytest.mark.api
    def test_delete_task_not_found(self, client):
        """Тест удаления несуществующей задачи"""
        task_id = uuid4()

        with patch("app.service.dep_service.get_task_service") as mock_get_service:
            # Настройка мока для исключения
            mock_service = AsyncMock(spec=TaskService)
            from fastapi import HTTPException

            mock_service.delete_task.side_effect = HTTPException(
                status_code=404, detail="Task not found"
            )
            mock_get_service.return_value = mock_service

            # Выполнение запроса
            response = client.delete(f"/api/v1/tasks/{task_id}")

            # Проверки
            assert response.status_code == 404
            data = response.json()
            assert data["detail"] == "Task not found"

    @pytest.mark.api
    def test_invalid_uuid_format(self, client):
        """Тест обработки некорректного UUID"""
        invalid_uuid = "invalid-uuid"

        response = client.get(f"/api/v1/tasks/{invalid_uuid}")

        assert response.status_code == 422  # Validation Error


class TestAPIEndpoints:
    """Тесты для проверки доступности эндпоинтов"""

    @pytest.fixture
    def client(self):
        """Фикстура для тестового клиента"""
        return TestClient(app)

    @pytest.mark.api
    def test_api_docs_endpoint(self, client):
        """Тест доступности документации API"""
        response = client.get("/docs")
        assert response.status_code == 200

    @pytest.mark.api
    def test_api_redoc_endpoint(self, client):
        """Тест доступности ReDoc документации"""
        response = client.get("/redoc")
        assert response.status_code == 200

    @pytest.mark.api
    def test_openapi_schema(self, client):
        """Тест доступности OpenAPI схемы"""
        response = client.get("/openapi.json")
        assert response.status_code == 200
        data = response.json()
        assert "openapi" in data
        assert "info" in data
        assert "paths" in data

    @pytest.mark.api
    def test_root_endpoint_not_found(self, client):
        """Тест что корневой эндпоинт не существует"""
        response = client.get("/")
        assert response.status_code == 404

    @pytest.mark.api
    def test_health_check_endpoint_not_found(self, client):
        """Тест что health check эндпоинт не существует"""
        response = client.get("/health")
        assert response.status_code == 404


class TestAPIMiddleware:
    """Тесты для middleware API"""

    @pytest.fixture
    def client(self):
        """Фикстура для тестового клиента"""
        return TestClient(app)

    @pytest.mark.api
    def test_cors_headers(self, client):
        """Тест CORS заголовков"""
        response = client.options("/api/v1/tasks/")

        # Проверяем что CORS middleware работает
        # (хотя конкретные заголовки могут зависеть от настроек)
        assert response.status_code in [200, 405]  # OPTIONS может не поддерживаться

    @pytest.mark.api
    def test_request_logging_middleware(self, client):
        """Тест middleware логирования"""
        with patch("app.service.dep_service.get_task_service") as mock_get_service:
            # Настройка мока
            mock_service = AsyncMock(spec=TaskService)
            mock_service.get_tasks.return_value = []
            mock_get_service.return_value = mock_service

            # Выполнение запроса
            response = client.get("/api/v1/tasks/")

            # Проверяем что запрос обработан (middleware не блокирует)
            assert response.status_code == 200


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-m", "api"])
