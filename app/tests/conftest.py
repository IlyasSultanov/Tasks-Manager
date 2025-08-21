"""
Configuration and fixtures for tests
"""

import pytest
import asyncio
from unittest.mock import AsyncMock, MagicMock
from uuid import uuid4
from datetime import datetime, timezone
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.pool import StaticPool

# Import application components
from app.schemas.schemas import TaskCreate, TaskUpdate, Task, TaskStatus
from app.models.models import TaskModel, TaskStatus as ModelTaskStatus
from app.service.service import TaskService
from app.db.base_class import BaseModel


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


@pytest.fixture
def sample_task_model():
    """Фикстура с моделью тестовой задачи"""
    return TaskModel(
        id=uuid4(),
        title="Sample Task",
        description="Sample Description",
        status=ModelTaskStatus.CREATED,
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc),
    )


@pytest.fixture
def sample_task_create_schema():
    """Фикстура с Pydantic схемой для создания задачи"""
    return TaskCreate(title="Sample Task", description="Sample Description")


@pytest.fixture
def sample_task_update_schema():
    """Фикстура с Pydantic схемой для обновления задачи"""
    return TaskUpdate(title="Updated Sample Task", status=TaskStatus.IN_PROGRESS)


@pytest.fixture
def sample_task_response_schema(sample_task_model):
    """Фикстура с Pydantic схемой ответа задачи"""
    return Task(
        id=sample_task_model.id,
        title=sample_task_model.title,
        description=sample_task_model.description,
        status=TaskStatus.CREATED,
        created_at=sample_task_model.created_at,
        updated_at=sample_task_model.updated_at,
    )


@pytest.fixture
def mock_db_session():
    """Фикстура для мока сессии базы данных"""
    return AsyncMock(spec=AsyncSession)


@pytest.fixture
def mock_task_service(mock_db_session):
    """Фикстура для мока TaskService"""
    return TaskService(mock_db_session)


@pytest.fixture
def sample_tasks_list():
    """Фикстура со списком тестовых задач"""
    return [
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
        TaskModel(
            id=uuid4(),
            title="Task 3",
            description="Description 3",
            status=ModelTaskStatus.COMPLETED,
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc),
        ),
    ]


@pytest.fixture
def test_uuid():
    """Фикстура с тестовым UUID"""
    return uuid4()


@pytest.fixture
def invalid_uuid():
    """Фикстура с некорректным UUID"""
    return "invalid-uuid-format"


@pytest.fixture
def mock_db_result():
    """Фикстура для мока результата запроса к БД"""
    mock_result = MagicMock()
    mock_result.scalars.return_value.all.return_value = []
    mock_result.scalar_one_or_none.return_value = None
    return mock_result


@pytest.fixture
def mock_db_result_with_task(sample_task_model):
    """Фикстура для мока результата запроса к БД с задачей"""
    mock_result = MagicMock()
    mock_result.scalars.return_value.all.return_value = [sample_task_model]
    mock_result.scalar_one_or_none.return_value = sample_task_model
    return mock_result


@pytest.fixture
def mock_db_result_with_tasks(sample_tasks_list):
    """Фикстура для мока результата запроса к БД со списком задач"""
    mock_result = MagicMock()
    mock_result.scalars.return_value.all.return_value = sample_tasks_list
    mock_result.scalar_one_or_none.return_value = sample_tasks_list[0]
    return mock_result


@pytest.fixture
def mock_db_result_not_found():
    """Фикстура для мока результата запроса к БД (задача не найдена)"""
    mock_result = MagicMock()
    mock_result.scalars.return_value.all.return_value = []
    mock_result.scalar_one_or_none.return_value = None
    return mock_result


@pytest.fixture
def sample_task_json():
    """Фикстура с JSON данными задачи"""
    return {
        "id": str(uuid4()),
        "title": "JSON Task",
        "description": "JSON Description",
        "status": "created",
        "created_at": "2024-01-01T00:00:00Z",
        "updated_at": "2024-01-01T00:00:00Z",
    }


@pytest.fixture
def sample_task_create_json():
    """Фикстура с JSON данными для создания задачи"""
    return {"title": "Create Task", "description": "Create Description"}


@pytest.fixture
def sample_task_update_json():
    """Фикстура с JSON данными для обновления задачи"""
    return {"title": "Update Task", "status": "in_progress"}


@pytest.fixture
def invalid_task_data():
    """Фикстура с некорректными данными задачи"""
    return {"title": "", "description": "Valid Description"}  # Пустой заголовок


@pytest.fixture
def missing_required_fields_data():
    """Фикстура с отсутствующими обязательными полями"""
    return {"title": "Only Title"}  # Отсутствует description


@pytest.fixture
def invalid_status_data():
    """Фикстура с некорректным статусом"""
    return {
        "title": "Valid Title",
        "description": "Valid Description",
        "status": "invalid_status",
    }


@pytest.fixture
def pagination_params():
    """Фикстура с параметрами пагинации"""
    return {"skip": 10, "limit": 5}


@pytest.fixture
def large_pagination_params():
    """Фикстура с большими параметрами пагинации"""
    return {"skip": 100, "limit": 1000}


@pytest.fixture
def negative_pagination_params():
    """Фикстура с отрицательными параметрами пагинации"""
    return {"skip": -10, "limit": -5}


@pytest.fixture
def mock_async_session():
    """Фикстура для создания мока асинхронной сессии"""
    session = AsyncMock(spec=AsyncSession)
    session.add = MagicMock()
    session.commit = AsyncMock()
    session.refresh = AsyncMock()
    session.delete = MagicMock()
    session.rollback = AsyncMock()
    session.close = AsyncMock()
    return session


@pytest.fixture
def mock_async_session_with_error():
    """Фикстура для создания мока асинхронной сессии с ошибкой"""
    session = AsyncMock(spec=AsyncSession)
    session.add = MagicMock()
    session.commit = AsyncMock(side_effect=Exception("Database error"))
    session.refresh = AsyncMock()
    session.delete = MagicMock()
    session.rollback = AsyncMock()
    session.close = AsyncMock()
    return session


@pytest.fixture
def sample_error_response():
    """Фикстура с примером ответа об ошибке"""
    return {"detail": "Task not found"}


@pytest.fixture
def sample_validation_error_response():
    """Фикстура с примером ответа об ошибке валидации"""
    return {
        "detail": [
            {
                "loc": ["body", "title"],
                "msg": "field required",
                "type": "value_error.missing",
            }
        ]
    }


@pytest.fixture
def test_environment_vars():
    """Фикстура с тестовыми переменными окружения"""
    return {
        "PROJECT_NAME": "Test Task Manager",
        "VERSION": "1.0.0-test",
        "DEBUG": "true",
        "DATABASE_URL": "postgresql://test:test@localhost/testdb",
    }


@pytest.fixture
def empty_environment_vars():
    """Фикстура с пустыми переменными окружения"""
    return {}


@pytest.fixture
def invalid_environment_vars():
    """Фикстура с некорректными переменными окружения"""
    return {"DEBUG": "invalid_boolean", "DATABASE_URL": "invalid_url"}


# Маркеры для категоризации тестов
def pytest_configure(config):
    """Конфигурация маркеров pytest"""
    config.addinivalue_line("markers", "unit: mark test as unit test")
    config.addinivalue_line("markers", "integration: mark test as integration test")
    config.addinivalue_line("markers", "api: mark test as API test")
    config.addinivalue_line("markers", "slow: mark test as slow running test")
    config.addinivalue_line("markers", "database: mark test as database test")


# Фикстуры для тестов производительности
@pytest.fixture
def performance_test_data():
    """Фикстура с данными для тестов производительности"""
    return {
        "large_title": "A" * 1000,  # Очень длинный заголовок
        "large_description": "B" * 10000,  # Очень длинное описание
        "normal_title": "Normal Title",
        "normal_description": "Normal Description",
    }


@pytest.fixture
def stress_test_data():
    """Фикстура с данными для стресс-тестов"""
    return {"tasks_count": 100, "concurrent_requests": 10, "timeout": 30}


# Фикстуры для тестов безопасности
@pytest.fixture
def security_test_data():
    """Фикстура с данными для тестов безопасности"""
    return {
        "sql_injection": "'; DROP TABLE tasks; --",
        "xss_payload": "<script>alert('XSS')</script>",
        "path_traversal": "../../../etc/passwd",
        "command_injection": "; rm -rf /;",
    }


# Фикстуры для тестов граничных случаев
@pytest.fixture
def boundary_test_data():
    """Фикстура с данными для тестов граничных случаев"""
    return {
        "empty_string": "",
        "whitespace_only": "   ",
        "max_length_string": "A" * 200,  # Максимальная длина title
        "unicode_string": "Задача с кириллицей 🚀",
        "special_chars": "!@#$%^&*()_+-=[]{}|;':\",./<>?",
    }
