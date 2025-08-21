# Тесты для Task Manager

Этот каталог содержит unit тесты для приложения Task Manager.

## Структура тестов

```
app/tests/
├── __init__.py          # Пакет тестов
├── conftest.py          # Конфигурация и фикстуры pytest
├── tests.py             # Основные unit тесты
├── test_api.py          # API тесты
└── README.md            # Этот файл
```

## Установка зависимостей для тестирования

```bash
# Установка тестовых зависимостей
poetry install --with test

# Или с pip
pip install pytest pytest-asyncio httpx pytest-mock aiosqlite
```

## Запуск тестов

### Запуск всех тестов
```bash
pytest
```

### Запуск с подробным выводом
```bash
pytest -v
```

### Запуск конкретного файла тестов
```bash
pytest app/tests/tests.py -v
pytest app/tests/test_api.py -v
```

### Запуск тестов по категориям
```bash
# Только unit тесты
pytest -m unit

# Только API тесты
pytest -m api

# Только интеграционные тесты
pytest -m integration

# Исключение медленных тестов
pytest -m "not slow"
```

### Запуск с покрытием кода
```bash
pytest --cov=app --cov-report=html
pytest --cov=app --cov-report=term-missing
```

### Запуск с параллельным выполнением
```bash
pytest -n auto
```

## Категории тестов

### Unit тесты (`@pytest.mark.unit`)
- Тесты отдельных компонентов
- Мокирование зависимостей
- Быстрое выполнение

### API тесты (`@pytest.mark.api`)
- Тесты HTTP эндпоинтов
- Использование TestClient
- Проверка ответов API

### Интеграционные тесты (`@pytest.mark.integration`)
- Тесты взаимодействия компонентов
- Может требовать тестовую БД

### Медленные тесты (`@pytest.mark.slow`)
- Тесты производительности
- Стресс-тесты
- Тесты с реальной БД

## Фикстуры

Основные фикстуры определены в `conftest.py`:

- `sample_task_data` - данные для тестовой задачи
- `mock_db_session` - мок сессии БД
- `mock_task_service` - мок сервиса задач
- `client` - тестовый HTTP клиент
- `sample_task_model` - модель тестовой задачи

## Примеры использования

### Тест сервиса
```python
@pytest.mark.asyncio
@pytest.mark.unit
async def test_create_task_success(self, mock_task_service, sample_task_data):
    result = await mock_task_service.create_task(sample_task_data)
    assert result.title == sample_task_data["title"]
```

### Тест API эндпоинта
```python
@pytest.mark.api
def test_create_task_api(self, client, sample_task_create_json):
    response = client.post("/api/v1/tasks/", json=sample_task_create_json)
    assert response.status_code == 200
```

### Тест с фикстурами
```python
@pytest.mark.unit
def test_task_model_creation(self, sample_task_model):
    assert sample_task_model.title == "Sample Task"
    assert sample_task_model.status == ModelTaskStatus.CREATED
```

## Конфигурация

### pytest.ini
Основные настройки pytest находятся в корне проекта в файле `pytest.ini`:

- `testpaths = app/tests` - путь к тестам
- `python_files = test_*.py` - паттерн файлов тестов
- `asyncio_mode = auto` - автоматический режим для асинхронных тестов
- `addopts = -v --tb=short` - опции по умолчанию

### Маркеры
- `unit` - unit тесты
- `integration` - интеграционные тесты
- `api` - API тесты
- `slow` - медленные тесты
- `database` - тесты с БД

## Лучшие практики

### 1. Именование тестов
```python
def test_create_task_success(self):
    """Тест успешного создания задачи"""
    pass

def test_create_task_with_empty_title_should_fail(self):
    """Тест создания задачи с пустым заголовком должно завершиться ошибкой"""
    pass
```

### 2. Использование фикстур
```python
@pytest.fixture
def sample_task(self):
    return TaskModel(title="Test", description="Test")

def test_task_creation(self, sample_task):
    assert sample_task.title == "Test"
```

### 3. Мокирование зависимостей
```python
@patch('app.service.dep_service.get_task_service')
def test_api_endpoint(self, mock_get_service):
    mock_service = AsyncMock()
    mock_get_service.return_value = mock_service
    # тест
```

### 4. Асинхронные тесты
```python
@pytest.mark.asyncio
async def test_async_function(self):
    result = await some_async_function()
    assert result is not None
```

## Отладка тестов

### Запуск с отладкой
```bash
pytest -s --pdb
```

### Запуск конкретного теста
```bash
pytest app/tests/tests.py::TestTaskService::test_create_task_success -v
```

### Вывод подробной информации об ошибках
```bash
pytest -vv --tb=long
```

## CI/CD интеграция

### GitHub Actions
```yaml
- name: Run tests
  run: |
    poetry install --with test
    pytest --cov=app --cov-report=xml
```

### GitLab CI
```yaml
test:
  script:
    - poetry install --with test
    - pytest --cov=app
```

## Покрытие кода

### Генерация отчета о покрытии
```bash
pytest --cov=app --cov-report=html --cov-report=term
```

### Минимальное покрытие
```bash
pytest --cov=app --cov-fail-under=80
```

## Полезные команды

```bash
# Показать доступные маркеры
pytest --markers

# Показать информацию о тестах без выполнения
pytest --collect-only

# Запуск тестов с профилированием
pytest --durations=10

# Запуск тестов с повторением при неудаче
pytest --lf --ff
```

## Troubleshooting

### Проблемы с импортами
Убедитесь, что PYTHONPATH включает корень проекта:
```bash
export PYTHONPATH="${PYTHONPATH}:$(pwd)"
```

### Проблемы с асинхронными тестами
Проверьте, что установлен `pytest-asyncio`:
```bash
pip install pytest-asyncio
```

### Проблемы с моками
Убедитесь, что пути к мокам корректны:
```python
@patch('app.service.dep_service.get_task_service')  # Правильно
# @patch('service.dep_service.get_task_service')   # Неправильно
```
