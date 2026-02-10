# services/auth_service.py
import requests
import json
from typing import Optional, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
import aiohttp
import asyncio

from models.user import User
from schemas.user import ExternalUserInfo

class AuthService:
    def __init__(self, external_auth_url: str = "https://intranet.emk.org.ru/api/auth_router/check"):
        self.external_auth_url = external_auth_url

    async def get_user_info(self, session_id: str) -> Optional[Dict[str, Any]]:
        """
        Получение информации о пользователе из внешней системы
        """
        cookies = {'session_id': session_id}

        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(self.external_auth_url, cookies=cookies) as response:
                    if response.status == 200:
                        return await response.json()
        except Exception as e:
            print(f"Ошибка при запросе к внешнему API: {e}")

        return None

    def parse_user_info(self, user_info: Dict[str, Any]) -> ExternalUserInfo:
        """
        Парсинг информации о пользователе из внешней системы
        """
        # Получаем ФИО
        full_name = ''
        if 'full_name' in user_info: full_name = user_info['full_name']

        if 'fio' in user_info:
            fio = user_info['full_name']

            last_name = fio.get('LAST_NAME', '')
            first_name = fio.get('NAME', '')
            middle_name = fio.get('SECOND_NAME', '')

            full_name = f"{last_name} {first_name} {middle_name}".strip()

        return ExternalUserInfo(
            id=int(user_info.get('ID')),
            full_name=full_name,
            position=user_info.get('WORK_POSITION'),
            department=user_info.get('uf_department') or user_info.get('UF_DEPARTMENT')
        )

    async def get_or_create_user(
            self,
            db: AsyncSession,
            session_id: str
    ) -> Optional[User]:
        """
        Получение или создание пользователя на основе session_id
        """
        # Получаем информацию из внешней системы
        user_info = await self.get_user_info(session_id)
        if not user_info:
            return None

        # Парсим информацию
        parsed_info = self.parse_user_info(user_info)

        if not parsed_info.external_id:
            return None

        # Ищем пользователя в нашей БД
        result = await db.execute(
            select(User).where(User.id == parsed_info.id)
        )
        user = result.scalar_one_or_none()

        if user:
            # Обновляем последний логин
            user.last_login = func.now()
            await db.commit()
            await db.refresh(user)
            return user

        # Создаем нового пользователя
        new_user = User(
            id=parsed_info.id,
            full_name=parsed_info.full_name,
            position=parsed_info.position,
            department=parsed_info.department,
            is_admin=False,
            last_login=func.now()
        )

        db.add(new_user)
        await db.commit()
        await db.refresh(new_user)

        return new_user

# Создаем экземпляр сервиса
auth_service = AuthService()