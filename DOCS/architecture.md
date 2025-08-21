# Архитектура проекта Task Manager

## Обзор проекта

Task Manager - это REST API сервис для управления задачами, построенный на FastAPI с использованием асинхронной архитектуры и PostgreSQL в качестве базы данных.

## Технологический стек

- **Framework**: FastAPI 0.116.1
- **Database**: PostgreSQL 15 (asyncpg)
- **ORM**: SQLAlchemy 2.0.43 (async)
- **Validation**: Pydantic
- **Configuration**: Pydantic Settings
- **Server**: Uvicorn
- **Containerization**: Docker & Docker Compose
- **Package Manager**: Poetry

## Структура проекта

```
Task_Manager/
├── app/                          # Основной код приложения
│   ├── __init__.py
│   ├── main.py                   # Точка входа приложения
│   ├── api/                      # API слои
│   │   └── v1/
│   │       ├── __init__.py
│   │       └── api.py            # API роутер v1
│   ├── config/                   # Конфигурация
│   │   ├── __init__.py
│   │   └── config.py             # Настройки приложения
│   ├── db/                       # Слой базы данных
│   │   ├── __init__.py
│   │   ├── base_class.py         # Базовая модель
│   │   ├── base.py               # Базовый класс SQLAlchemy
│   │   └── session.py            # Управление сессиями БД
│   ├── middleware/               # Middleware
│   │   ├── __init__.py
│   │   └── logging.py            # Логирование
│   ├── models/                   # Модели данных
│   │   ├── __init__.py
│   │   └── models.py             # SQLAlchemy модели
│   ├── router/                   # Роутеры
│   │   ├── __init__.py
│   │   └── router.py             # Роутеры задач
│   ├── schemas/                  # Pydantic схемы
│   │   ├── __init__.py
│   │   └── schemas.py            # Схемы валидации
│   └── service/                  # Бизнес-логика
│       ├── __init__.py
│       ├── dep_service.py        # Dependency injection
│       └── service.py            # Сервисы
├── docker-compose.yml            # Docker Compose конфигурация
├── Dockerfile                    # Docker образ
├── pyproject.toml               # Зависимости и метаданные
└── DOCS/                        # Документация
    └── architecture.md          # Этот файл
```

## Архитектурные слои

### 1. Presentation Layer (API)

**Файлы**: `app/main.py`, `app/api/v1/api.py`, `app/router/router.py`

- **FastAPI приложение** с настройкой CORS, middleware и роутеров
- **API версионирование** через префикс `/api/v1`
- **Автоматическая документация** через Swagger UI (`/docs`) и ReDoc (`/redoc`)
- **Lifespan management** для инициализации и очистки ресурсов

### 2. Business Logic Layer (Service)

**Файлы**: `app/service/service.py`, `app/service/dep_service.py`

- **TaskService** - основной сервис для работы с задачами
- **CRUD операции**: создание, чтение, обновление, удаление задач
- **Dependency injection** для внедрения зависимостей
- **Обработка ошибок** с HTTP исключениями

### 3. Data Access Layer (Models & Database)

**Файлы**: `app/models/models.py`, `app/db/`

- **SQLAlchemy модели** с асинхронной поддержкой
- **BaseModel** с общими полями (id, created_at, updated_at, deleted_at)
- **Асинхронные сессии** для работы с базой данных
- **Soft delete** поддержка

### 4. Validation Layer (Schemas)

**Файлы**: `app/schemas/schemas.py`

- **Pydantic схемы** для валидации входных и выходных данных
- **TaskBase**, **TaskCreate**, **TaskUpdate**, **Task** схемы
- **Enum для статусов** задач

## Модель данных

### Task (Задача)

```python
class TaskModel(BaseModel):
    __tablename__ = "tasks"
    
    title: str                    # Заголовок задачи
    description: str              # Описание задачи
    status: TaskStatus            # Статус задачи
    id: UUID                      # Уникальный идентификатор
    created_at: datetime          # Время создания
    updated_at: datetime          # Время обновления
    deleted_at: datetime | None   # Время удаления (soft delete)
```

### Статусы задач

```python
class TaskStatus(str, Enum):
    CREATED = "created"           # Создана
    IN_PROGRESS = "in_progress"   # В работе
    COMPLETED = "completed"       # Завершена
```

## API Endpoints

### Tasks API (`/api/v1/tasks`)

| Метод | Endpoint | Описание | Параметры |
|-------|----------|----------|-----------|
| POST | `/` | Создать задачу | `TaskCreate` |
| GET | `/` | Получить список задач | `skip`, `limit` |
| GET | `/{task_id}` | Получить задачу по ID | `task_id` |
| PUT | `/{task_id}` | Обновить задачу | `task_id`, `TaskUpdate` |
| DELETE | `/{task_id}` | Удалить задачу | `task_id` |

## Конфигурация

**Файл**: `app/config/config.py`

```python
class Config(BaseSettings):
    project_name: str = "Task Manager"
    version: str = "1.0.0"
    db_url: str                    # URL базы данных
    debug: bool = False            # Режим отладки
```

### Переменные окружения

- `DATABASE_URL` - URL подключения к PostgreSQL
- `PROJECT_NAME` - Название проекта
- `VERSION` - Версия приложения
- `DEBUG` - Режим отладки

## База данных

### PostgreSQL
- **Версия**: 15-alpine
- **Порт**: 5432
- **Асинхронное подключение** через asyncpg
- **Connection pooling** с предварительной проверкой соединений

### Миграции
- **Автоматическое создание таблиц** при запуске приложения
- **BaseModel.metadata.create_all()** в lifespan

## Docker & Deployment

### Docker Compose
- **app** - FastAPI приложение
- **postgres** - PostgreSQL база данных
- **Volumes** для персистентности данных

### Переменные окружения для Docker
```env
DATABASE_URL=postgresql://user:password@postgres:5432/dbname
POSTGRES_USER=user
POSTGRES_PASSWORD=password
POSTGRES_DB=dbname
```

## Middleware

### LoggingMiddleware
- **Логирование запросов** и ответов
- **Время выполнения** запросов
- **Статус коды** ответов

### CORS Middleware
- **Разрешенные origins**: `["*"]`
- **Поддержка credentials**
- **Все HTTP методы** разрешены

## Обработка ошибок

- **HTTP 404** - Задача не найдена
- **HTTP 500** - Внутренние ошибки сервера
- **Валидация данных** через Pydantic
- **Логирование ошибок** с детальной информацией

## Безопасность

- **UUID** для идентификаторов (защита от enumeration attacks)
- **Soft delete** для сохранения истории
- **Валидация входных данных** через Pydantic
- **CORS настройки** для веб-клиентов

## Производительность

- **Асинхронная архитектура** для высокой производительности
- **Connection pooling** для эффективного использования БД
- **Пагинация** для больших списков задач
- **Индексы** на первичных ключах

## Мониторинг и логирование

- **Structured logging** с уровнем INFO
- **Lifespan events** для мониторинга состояния приложения
- **Database health checks** при запуске
- **Request/Response logging** через middleware

## Разработка

### Запуск в режиме разработки
```bash
# С Docker Compose
docker-compose up

# Локально
poetry install
poetry run python app/main.py
```

### API документация
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## Тестирование

### Установка зависимостей для тестирования
```bash
poetry install --with test
```

### Запуск тестов
```bash
# Все тесты
pytest

# Unit тесты
pytest -m unit

# API тесты
pytest -m api

# С покрытием кода
pytest --cov=app --cov-report=html
```

### Структура тестов
```
app/tests/
├── __init__.py          # Пакет тестов
├── conftest.py          # Конфигурация и фикстуры
├── tests.py             # Основные unit тесты
├── test_api.py          # API тесты
└── README.md            # Документация тестов
```

### Категории тестов
- **Unit тесты** - тестирование отдельных компонентов
- **API тесты** - тестирование HTTP эндпоинтов
- **Интеграционные тесты** - тестирование взаимодействия компонентов
- **Медленные тесты** - тесты производительности и стресс-тесты

## Планы развития

1. **Аутентификация и авторизация**
2. **Теги и категории для задач**
3. **Приоритеты задач**
4. **Назначение задач пользователям**
5. **Уведомления и дедлайны**
6. **API rate limiting**
7. **Кэширование**
8. **Метрики и мониторинг**
