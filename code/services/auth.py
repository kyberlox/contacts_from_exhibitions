# dependencies/auth.py
from fastapi import Depends, HTTPException, status, Cookie
from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from models.database import get_db
from models.user import User

async def get_current_user(
        session_id: Optional[str] = Cookie(None, alias="session_id"),
        current_user_id: Optional[int] = Cookie(None, alias="user_id"),
        db: AsyncSession = Depends(get_db)
) -> Optional[User]:
    """
    Dependency для получения текущего пользователя из куки
    """
    print(f"session_id: {session_id}, current_user_id: {current_user_id}")
    if not current_user_id or not session_id:
        return None

    try:
        # Ищем пользователя в БД
        result = await db.execute(
            select(User).where(User.id == current_user_id)
        )
        user = result.scalar_one_or_none()

        if not user:
            return None

        return user

    except Exception as e:
        # В случае ошибки возвращаем None
        print(f"Ошибка при получении пользователя: {e}")
        return None

async def get_current_active_user(
        current_user: Optional[User] = Depends(get_current_user)
) -> Optional[User]:
    """
    Проверяет, что пользователь активен
    """
    if current_user:
        return None
    return current_user

async def require_admin(
        current_user: Optional[User] = Depends(get_current_active_user)
) -> User:
    """
    Требует, чтобы пользователь был администратором
    """
    if not current_user or not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Требуются права администратора"
        )
    return current_user

async def require_auth(
        current_user: Optional[User] = Depends(get_current_active_user)
) -> User:
    """
    Требует авторизации (любой пользователь)
    """
    if not current_user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Требуется авторизация"
        )
    return current_user

async def get_optional_user(
        session_id: Optional[str] = Cookie(None, alias="session_id"),
        current_user_id: Optional[int] = Cookie(None, alias="user_id"),
        db: AsyncSession = Depends(get_db)
) -> Optional[User]:
    """
    Dependency для получения пользователя (опционально)
    Возвращает пользователя или None если не авторизован
    """
    return await get_current_user(session_id, current_user_id, db)