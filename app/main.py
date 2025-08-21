import logging
import asyncio
from contextlib import asynccontextmanager
from sqlalchemy import text

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from config.config import settings
from router import router
from middleware import LoggingMiddleware
from db.base_class import BaseModel
from db.session import async_engine
from api.v1 import router

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Проверка подключения к БД
    try:
        async with async_engine.connect() as conn:
            await conn.execute(text("SELECT 1"))
        logger.info("✅ Подключение к БД успешно")
    except Exception as e:
        logger.error("❌ Ошибка подключения к БД: %s", e)
        raise RuntimeError("Не удалось подключиться к БД") from e

    # Создание таблиц
    try:
        async with async_engine.begin() as conn:
            await conn.run_sync(BaseModel.metadata.create_all)
        logger.info("✅ Таблицы созданы")
    except Exception as e:
        logger.error("❌ Ошибка создания таблиц: %s", e)
        raise

    yield

    # Завершение
    await async_engine.dispose()
    logger.info("🔧 БД отключена")


app = FastAPI(
    title=settings.project_name,
    version=settings.version,
    debug=settings.debug,
    description="API for task management",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan,
)

app.add_middleware(LoggingMiddleware)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router, prefix="/api/v1")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)