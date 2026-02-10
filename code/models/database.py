# database.py
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from typing import AsyncGenerator
import os
from dotenv import load_dotenv

load_dotenv()

user = os.getenv('user')
pswd = os.getenv('pswd')

# Используем asyncpg драйвер для PostgreSQL
DATABASE_URL = f'postgresql+asyncpg://{user}:{pswd}@postgres/pdb'

# Создаем асинхронный движок
engine = create_async_engine(
    DATABASE_URL,
    echo=True,  # Включаем логирование SQL-запросов (для разработки)
    future=True,
    pool_size=20,
    max_overflow=40,
    pool_pre_ping=True,
    pool_recycle=3600,
)

# Создаем фабрику асинхронных сессий
AsyncSessionLocal = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False,
)

# Dependency для FastAPI
async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """
    Асинхронный генератор для получения сессии БД.
    Используется как dependency в FastAPI роутах.
    """
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()

# Функция для создания таблиц
async def create_tables():
    """
    Создает все таблицы в БД.
    ВНИМАНИЕ: В продакшене используйте миграции (Alembic) вместо этой функции.
    """
    from .base import Base
    # Импортируем все модели, чтобы они были зарегистрированы в Base.metadata
    from .file import File
    from .exhibition import Exhibition
    from .contact import Contact, contact_file_association

    try:
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
            print("✅ Таблицы успешно созданы")
    except Exception as e:
        print(f"❌ Ошибка при создании таблиц: {e}")

# Функция для закрытия соединений
async def close_connection():
    """Закрывает соединения с БД при завершении приложения."""
    await engine.dispose()