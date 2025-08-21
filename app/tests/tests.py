"""
Unit tests for Task Manager application
"""

import pytest
import asyncio
from unittest.mock import AsyncMock, MagicMock, patch
from uuid import uuid4, UUID
from datetime import datetime, timezone
from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

# Import application components
from app.schemas.schemas import TaskCreate, TaskUpdate, Task, TaskStatus
from app.models.models import TaskModel, TaskStatus as ModelTaskStatus
from app.service.service import TaskService
from app.config.config import Config


class TestTaskSchemas:
    """Тесты для Pydantic схем"""

    @pytest.mark.unit
    def test_task_create_schema(self):
        """Тест создания схемы TaskCreate"""
        task_data = {"title": "Test Task", "description": "Test Description"}
        task = TaskCreate(**task_data)

        assert task.title == "Test Task"
        assert task.description == "Test Description"

    @pytest.mark.unit
    def test_task_update_schema_partial(self):
        """Тест частичного обновления схемы TaskUpdate"""
        task_data = {"title": "Updated Title"}
        task = TaskUpdate(**task_data)

        assert task.title == "Updated Title"
        assert task.description is None
        assert task.status is None

    @pytest.mark.unit
    def test_task_update_schema_full(self):
        """Тест полного обновления схемы TaskUpdate"""
        task_data = {
            "title": "Updated Title",
            "description": "Updated Description",
            "status": TaskStatus.IN_PROGRESS,
        }
        task = TaskUpdate(**task_data)

        assert task.title == "Updated Title"
        assert task.description == "Updated Description"
        assert task.status == TaskStatus.IN_PROGRESS

    @pytest.mark.unit
    def test_task_schema_from_model(self):
        """Тест создания Task схемы из модели"""
        task_id = uuid4()
        created_at = datetime.now(timezone.utc)
        updated_at = datetime.now(timezone.utc)

        task_data = {
            "id": task_id,
            "title": "Test Task",
            "description": "Test Description",
            "status": TaskStatus.CREATED,
            "created_at": created_at,
            "updated_at": updated_at,
        }
        task = Task(**task_data)

        assert task.id == task_id
        assert task.title == "Test Task"
        assert task.description == "Test Description"
        assert task.status == TaskStatus.CREATED
        assert task.created_at == created_at
        assert task.updated_at == updated_at


class TestTaskModel:
    """Тесты для SQLAlchemy модели TaskModel"""

    @pytest.mark.unit
    def test_task_model_creation(self):
        """Тест создания модели TaskModel"""
        task = TaskModel(title="Test Task", description="Test Description")

        assert task.title == "Test Task"
        assert task.description == "Test Description"
        assert task.status == ModelTaskStatus.CREATED
        assert task.id is not None
        assert isinstance(task.id, UUID)

    @pytest.mark.unit
    def test_task_model_with_custom_status(self):
        """Тест создания модели TaskModel с кастомным статусом"""
        task = TaskModel(
            title="Test Task",
            description="Test Description",
            status=ModelTaskStatus.IN_PROGRESS,
        )

        assert task.status == ModelTaskStatus.IN_PROGRESS

    @pytest.mark.unit
    def test_task_model_repr(self):
        """Тест строкового представления модели"""
        task = TaskModel(title="Test Task", description="Test Description")

        repr_str = repr(task)
        assert "TaskModel" in repr_str
        assert str(task.id) in repr_str

    @pytest.mark.unit
    def test_task_model_to_dict(self):
        """Тест конвертации модели в словарь"""
        task = TaskModel(title="Test Task", description="Test Description")

        task_dict = task.to_dict()

        assert "id" in task_dict
        assert "title" in task_dict
        assert "description" in task_dict
        assert "status" in task_dict
        assert "created_at" in task_dict
        assert "updated_at" in task_dict
        assert task_dict["title"] == "Test Task"
        assert task_dict["description"] == "Test Description"


class TestTaskService:
    """Тесты для TaskService"""

    @pytest.fixture
    def mock_session(self):
        """Фикстура для мока сессии БД"""
        return AsyncMock(spec=AsyncSession)

    @pytest.fixture
    def task_service(self, mock_session):
        """Фикстура для TaskService с мок сессией"""
        return TaskService(mock_session)

    @pytest.fixture
    def sample_task(self):
        """Фикстура для примера задачи"""
        task_id = uuid4()
        return TaskModel(
            id=task_id,
            title="Test Task",
            description="Test Description",
            status=ModelTaskStatus.CREATED,
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc),
        )

    @pytest.mark.asyncio
    @pytest.mark.unit
    async def test_create_task_success(self, task_service, mock_session):
        """Тест успешного создания задачи"""
        task_data = TaskCreate(title="New Task", description="New Description")

        # Настройка мока
        mock_session.add = MagicMock()
        mock_session.commit = AsyncMock()
        mock_session.refresh = AsyncMock()

        # Выполнение
        result = await task_service.create_task(task_data)

        # Проверки
        assert result.title == "New Task"
        assert result.description == "New Description"
        assert result.status == ModelTaskStatus.CREATED
        mock_session.add.assert_called_once()
        mock_session.commit.assert_called_once()
        mock_session.refresh.assert_called_once()

    @pytest.mark.asyncio
    @pytest.mark.unit
    async def test_get_tasks_success(self, task_service, mock_session, sample_task):
        """Тест успешного получения списка задач"""
        # Настройка мока
        mock_result = MagicMock()
        mock_result.scalars.return_value.all.return_value = [sample_task]
        mock_session.execute = AsyncMock(return_value=mock_result)

        # Выполнение
        result = await task_service.get_tasks(skip=0, limit=10)

        # Проверки
        assert len(result) == 1
        assert result[0].title == "Test Task"
        mock_session.execute.assert_called_once()

    @pytest.mark.asyncio
    @pytest.mark.unit
    async def test_get_task_success(self, task_service, mock_session, sample_task):
        """Тест успешного получения задачи по ID"""
        task_id = sample_task.id

        # Настройка мока
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = sample_task
        mock_session.execute = AsyncMock(return_value=mock_result)

        # Выполнение
        result = await task_service.get_task(task_id)

        # Проверки
        assert result.id == task_id
        assert result.title == "Test Task"
        mock_session.execute.assert_called_once()

    @pytest.mark.asyncio
    @pytest.mark.unit
    async def test_get_task_not_found(self, task_service, mock_session):
        """Тест получения несуществующей задачи"""
        task_id = uuid4()

        # Настройка мока
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = None
        mock_session.execute = AsyncMock(return_value=mock_result)

        # Выполнение и проверка исключения
        with pytest.raises(HTTPException) as exc_info:
            await task_service.get_task(task_id)

        assert exc_info.value.status_code == 404
        assert exc_info.value.detail == "Task not found"

    @pytest.mark.asyncio
    @pytest.mark.unit
    async def test_update_task_success(self, task_service, mock_session, sample_task):
        """Тест успешного обновления задачи"""
        task_id = sample_task.id
        update_data = TaskUpdate(title="Updated Title", status=TaskStatus.IN_PROGRESS)

        # Настройка мока
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = sample_task
        mock_session.execute = AsyncMock(return_value=mock_result)
        mock_session.commit = AsyncMock()
        mock_session.refresh = AsyncMock()

        # Выполнение
        result = await task_service.update_task(task_id, update_data)

        # Проверки
        assert result.title == "Updated Title"
        assert result.status == ModelTaskStatus.IN_PROGRESS
        mock_session.commit.assert_called_once()
        mock_session.refresh.assert_called_once()

    @pytest.mark.asyncio
    @pytest.mark.unit
    async def test_update_task_not_found(self, task_service, mock_session):
        """Тест обновления несуществующей задачи"""
        task_id = uuid4()
        update_data = TaskUpdate(title="Updated Title")

        # Настройка мока
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = None
        mock_session.execute = AsyncMock(return_value=mock_result)

        # Выполнение и проверка исключения
        with pytest.raises(HTTPException) as exc_info:
            await task_service.update_task(task_id, update_data)

        assert exc_info.value.status_code == 404
        assert exc_info.value.detail == "Task not found"

    @pytest.mark.asyncio
    @pytest.mark.unit
    async def test_delete_task_success(self, task_service, mock_session, sample_task):
        """Тест успешного удаления задачи"""
        task_id = sample_task.id

        # Настройка мока
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = sample_task
        mock_session.execute = AsyncMock(return_value=mock_result)
        mock_session.delete = MagicMock()
        mock_session.commit = AsyncMock()

        # Выполнение
        result = await task_service.delete_task(task_id)

        # Проверки
        assert result is None
        mock_session.delete.assert_called_once_with(sample_task)
        mock_session.commit.assert_called_once()

    @pytest.mark.asyncio
    @pytest.mark.unit
    async def test_delete_task_not_found(self, task_service, mock_session):
        """Тест удаления несуществующей задачи"""
        task_id = uuid4()

        # Настройка мока
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = None
        mock_session.execute = AsyncMock(return_value=mock_result)

        # Выполнение и проверка исключения
        with pytest.raises(HTTPException) as exc_info:
            await task_service.delete_task(task_id)

        assert exc_info.value.status_code == 404
        assert exc_info.value.detail == "Task not found"


class TestConfig:
    """Тесты для конфигурации"""

    @pytest.mark.unit
    def test_config_default_values(self):
        """Тест значений по умолчанию конфигурации"""
        with patch.dict("os.environ", {}, clear=True):
            config = Config()

            assert config.project_name == "Task Manager"
            assert config.version == "1.0.0"
            assert config.debug is False

    @pytest.mark.unit
    def test_config_from_environment(self):
        """Тест загрузки конфигурации из переменных окружения"""
        env_vars = {
            "PROJECT_NAME": "Custom Task Manager",
            "VERSION": "2.0.0",
            "DEBUG": "true",
            "DATABASE_URL": "postgresql://test:test@localhost/test",
        }

        with patch.dict("os.environ", env_vars, clear=True):
            config = Config()

            assert config.project_name == "Custom Task Manager"
            assert config.version == "2.0.0"
            assert config.debug is True
            assert config.db_url == "postgresql://test:test@localhost/test"


class TestTaskStatus:
    """Тесты для enum статусов задач"""

    @pytest.mark.unit
    def test_task_status_values(self):
        """Тест значений enum TaskStatus"""
        assert TaskStatus.CREATED == "created"
        assert TaskStatus.IN_PROGRESS == "in_progress"
        assert TaskStatus.COMPLETED == "completed"

    @pytest.mark.unit
    def test_task_status_comparison(self):
        """Тест сравнения статусов"""
        assert TaskStatus.CREATED != TaskStatus.IN_PROGRESS
        assert TaskStatus.IN_PROGRESS != TaskStatus.COMPLETED
        assert TaskStatus.CREATED == "created"

    @pytest.mark.unit
    def test_task_status_in_model(self):
        """Тест использования статусов в модели"""
        task = TaskModel(
            title="Test Task",
            description="Test Description",
            status=ModelTaskStatus.IN_PROGRESS,
        )

        assert task.status == ModelTaskStatus.IN_PROGRESS
        assert task.status == "in_progress"


class TestIntegration:
    """Интеграционные тесты"""

    @pytest.mark.asyncio
    @pytest.mark.integration
    async def test_task_lifecycle(self):
        """Тест полного жизненного цикла задачи"""
        # Создание задачи
        task_data = TaskCreate(
            title="Integration Test Task", description="Integration Test Description"
        )

        # Проверка схемы
        assert task_data.title == "Integration Test Task"
        assert task_data.description == "Integration Test Description"

        # Создание модели
        task_model = TaskModel(title=task_data.title, description=task_data.description)

        assert task_model.title == task_data.title
        assert task_model.description == task_data.description
        assert task_model.status == ModelTaskStatus.CREATED

        # Обновление задачи
        update_data = TaskUpdate(
            title="Updated Integration Task", status=TaskStatus.IN_PROGRESS
        )

        # Симуляция обновления
        task_model.title = update_data.title
        task_model.status = ModelTaskStatus.IN_PROGRESS

        assert task_model.title == "Updated Integration Task"
        assert task_model.status == ModelTaskStatus.IN_PROGRESS

        # Создание схемы ответа
        response_task = Task(
            id=task_model.id,
            title=task_model.title,
            description=task_model.description,
            status=TaskStatus.IN_PROGRESS,
            created_at=task_model.created_at,
            updated_at=task_model.updated_at,
        )

        assert response_task.id == task_model.id
        assert response_task.title == "Updated Integration Task"
        assert response_task.status == TaskStatus.IN_PROGRESS


# Фикстуры для pytest
@pytest.fixture(scope="session")
def event_loop():
    """Создание event loop для асинхронных тестов"""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture
def sample_task_data():
    """Фикстура с данными для тестовой задачи"""
    return {"title": "Sample Task", "description": "Sample Description"}


@pytest.fixture
def sample_task_update_data():
    """Фикстура с данными для обновления задачи"""
    return {"title": "Updated Sample Task", "status": TaskStatus.IN_PROGRESS}


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
