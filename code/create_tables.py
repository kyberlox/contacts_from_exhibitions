# create_tables.py
import asyncio
import sys
from pathlib import Path

# Добавляем корневую директорию в PYTHONPATH
sys.path.append(str(Path(__file__).parent))

from database import create_tables, close_connection

async def main():
    """Создание всех таблиц в БД"""
    try:
        await create_tables()
        print("✅ Таблицы успешно созданы")
    except Exception as e:
        print(f"❌ Ошибка при создании таблиц: {e}")
    finally:
        await close_connection()

if __name__ == "__main__":
    asyncio.run(main())