# dependencies/active_exhibition.py
from fastapi import Depends, HTTPException, status, Cookie
from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from models.database import get_db
from models.exhibition import Exhibition

async def get_current_exhibition(
        db: AsyncSession = Depends(get_db)
) -> Optional[Exhibition]:
    """
    Dependency для получения текущего пользователя из куки
    """

    # Строим базовый запрос
    result = await db.execute(
            select(Exhibition).where(Exhibition.is_active == True)
        )

    

    try:
        # Ищем пользователя в БД
        
        exhibition_active = result.scalar_one_or_none()

        if exhibition_active is None:
            return None

        return exhibition_active.id

    except Exception as e:
        # В случае ошибки возвращаем None
        print(f"Ошибка при получении текущей выставки: {e}")
        return None