# routers/users.py
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, or_
from typing import List, Optional

from models.database import get_db
from models.user import User
from schemas.user import User as UserSchema, UserUpdate, UserShort
from schemas.base import PaginationParams, PaginatedResponse
from services.auth import require_admin, get_optional_user

router = APIRouter(prefix="/users", tags=["users"])

@router.get("/", response_model=PaginatedResponse)
async def get_users(
        pagination: PaginationParams = Depends(),
        search: Optional[str] = Query(None, description="Поиск по ФИО, должности, отделу"),
        is_admin: Optional[bool] = Query(None, description="Фильтр по админам"),
        _: User = Depends(require_admin),  # Проверка прав администратора
        db: AsyncSession = Depends(get_db)
):
    """Получение списка пользователей (только для администраторов)"""
    query = select(User)

    if search:
        search_pattern = f"%{search}%"
        query = query.where(
            or_(
                User.full_name.ilike(search_pattern),
                User.position.ilike(search_pattern),
                User.department.ilike(search_pattern),
                User.email.ilike(search_pattern)
            )
        )

    if is_admin is not None:
        query = query.where(User.is_admin == is_admin)

    # Сортировка по дате создания
    query = query.order_by(User.created_at.desc())

    # Общее количество
    total_query = select(func.count()).select_from(query.subquery())
    total_result = await db.execute(total_query)
    total = total_result.scalar()

    # Пагинация
    query = query.offset(pagination.skip).limit(pagination.limit)

    result = await db.execute(query)
    users = result.scalars().all()

    # Преобразуем вручную
    items = []
    for user in users:
        items.append({
            "id": user.id,
            "full_name": user.full_name,
            "position": user.position,
            "department": user.department,
            "is_admin": user.is_admin,
            "last_login": user.last_login,
            "created_at": user.created_at,
            "updated_at": user.updated_at,
        })

    return PaginatedResponse(
        total=total,
        skip=pagination.skip,
        limit=pagination.limit,
        items=items
    )

@router.get("/me", response_model=UserSchema)
async def get_current_user_info(
        current_user: Optional[User] = Depends(get_optional_user)
):
    """Получение информации о текущем пользователе"""
    if not current_user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Пользователь не авторизован"
        )
    return current_user


@router.get("/me_admin", response_model=UserSchema)
async def get_current_user_info(
        current_user: Optional[User] = Depends(get_optional_user)
):
    """Получение информации о текущем пользователе"""
    if not current_user:
        return {"is_admin" : False}
        
    return {"is_admin" : current_user.is_admin}

@router.get("/{user_id}", response_model=UserSchema)
async def get_user(
        user_id: int,
        _: User = Depends(require_admin),  # Проверка прав администратора
        db: AsyncSession = Depends(get_db)
):
    """Получение пользователя по ID (только для администраторов)"""
    result = await db.execute(
        select(User).where(User.id == user_id)
    )
    user = result.scalar_one_or_none()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Пользователь не найден"
        )

    return user

@router.put("/{user_id}", response_model=UserSchema)
async def update_user(
        user_id: int,
        user_data: UserUpdate,
        _: User = Depends(require_admin),  # Проверка прав администратора
        db: AsyncSession = Depends(get_db)
):
    """Обновление пользователя (только для администраторов)"""
    result = await db.execute(
        select(User).where(User.id == user_id)
    )
    user = result.scalar_one_or_none()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Пользователь не найден"
        )

    # Обновляем поля
    update_data = user_data.dict(exclude_unset=True)
    for field, value in update_data.items():
        if value is not None:
            setattr(user, field, value)

    await db.commit()
    await db.refresh(user)

    return user

@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(
        user_id: int,
        _: User = Depends(require_admin),  # Проверка прав администратора
        db: AsyncSession = Depends(get_db)
):
    """Удаление пользователя (только для администраторов)"""
    result = await db.execute(
        select(User).where(User.id == user_id)
    )
    user = result.scalar_one_or_none()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Пользователь не найден"
        )

    await db.delete(user)
    await db.commit()

    return None
