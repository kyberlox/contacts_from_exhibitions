# main.py
from fastapi import FastAPI, Response, Cookie, HTTPException, status, Depends, File, UploadFile, Form
from fastapi.responses import RedirectResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from contextlib import asynccontextmanager
from sqlalchemy.ext.asyncio import AsyncSession
import uvicorn
from pathlib import Path
from sqlalchemy import text  # Добавляем импорт text

from sqlalchemy import select, func
from datetime import datetime, timedelta
from typing import Dict, Any, Optional

from models.user import User

from models.database import engine, AsyncSessionLocal, create_tables, get_db

from routers import exhibitions_router, contacts_router, files_router, users_router

#OCR
from PIL import Image, ImageFilter, ImageEnhance
import pytesseract
import io
import tempfile
import subprocess
import os
import re

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Управление жизненным циклом приложения"""
    # Создаем таблицы при запуске
    #print("🔄 Проверка и создание таблиц БД...")
    await create_tables()
    #print("✅ Таблицы БД готовы")

    # Создаем директории для загрузки файлов
    Path("uploads").mkdir(parents=True, exist_ok=True)
    Path("uploads").mkdir(parents=True, exist_ok=True)
    Path("uploads").mkdir(parents=True, exist_ok=True)
    #print("✅ Директории для файлов созданы")

    # Проверяем соединение с БД
    try:
        async with AsyncSessionLocal() as session:
            await session.execute(text("SELECT 1"))  # Используем text()
        print("✅ Соединение с БД установлено")
    except Exception as e:
        print(f"❌ Ошибка подключения к БД: {e}")
        raise

    yield

    # Закрываем соединения при завершении
    await engine.dispose()
    #print("✅ Соединения с БД закрыты")

app = FastAPI(
    title="Exhibition Contacts API",
    description="API для сбора и управления контактами с выставок",
    version="1.0.0",
    docs_url="/api/docs",
    # redoc_url="/redoc",
    redoc_url=None,
    openapi_url="/api/openapi.json",
    lifespan=lifespan
)


# Настройка CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # В продакшене замените на конкретные домены
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Подключаем статические файлы
app.mount("/api/uploads", StaticFiles(directory="uploads"), name="uploads")

app.include_router(contacts_router, prefix="/api")
app.include_router(exhibitions_router, prefix="/api")
app.include_router(files_router, prefix="/api")
app.include_router(users_router, prefix="/api")


@app.post("/api/login")
async def login(
        user_data: Dict[str, Any],
        response: Response,
        db: AsyncSession = Depends(get_db)
):
    """
    Авторизация пользователя из внешней системы

    Принимает данные в формате:
    {
        "id": "external_user_id",
        "fio": {"last_name": "Иванов", "first_name": "Иван", "middle_name": "Иванович"},
        "department": "Отдел продаж",
        "position": "Менеджер",
        "session_id": "session_token_123"
    }
    """

    try:
        # Извлекаем данные
        external_id = int(user_data.get('id', None))
        fio_data = user_data.get('fio', {})
        department = user_data.get('department')
        position = user_data.get('position')
        session_id = user_data.get('session_id')

        if not external_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Не указан ID пользователя"
            )

        if not session_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Не указан session_id"
            )

        # Формируем ФИО
        last_name = fio_data.get('last_name', '')
        first_name = fio_data.get('first_name', '')
        middle_name = fio_data.get('middle_name', '')
        full_name = f"{last_name} {first_name} {middle_name}".strip()



        if not full_name:
            full_name = "Неизвестный пользователь"

        # Ищем пользователя в нашей БД по external_id
        result = await db.execute(
            select(User).where(User.id == external_id)
        )
        user = result.scalar_one_or_none()
        print(user)
        if user is not None:
            # Обновляем существующего пользователя
            user.full_name = full_name
            user.department = department
            user.position = position
            user.last_login = func.now()
        else:
            # Создаем нового пользователя
            user = User(
                id=external_id,
                full_name=full_name,
                department=department,
                position=position,
                is_admin=False,  # По умолчанию не админ
                last_login=func.now()
            )
            db.add(user)

        await db.commit()
        await db.refresh(user)

        # redirect_url = f"http://exhibitions.kyberlox.ru/users/me"
        #  # Создаем RedirectResponse
        # response = RedirectResponse(url=redirect_url)

        # Устанавливаем куки
        response.set_cookie(
            key="session_id",
            value=session_id,
            httponly=True,
            secure=False,  # В продакшене установите True
            samesite="lax",
            max_age=30 * 24 * 60 * 60  # 30 дней
        )

        response.set_cookie(
            key="user_id",
            value=str(external_id),
            httponly=True,
            secure=False,
            samesite="lax",
            max_age=30 * 24 * 60 * 60
        )

        return {
            "message": "Успешная авторизация",
            "user": {
                "id": user.id,
                "full_name": user.full_name,
                "department": user.department,
                "position": user.position,
                "is_admin": user.is_admin
            }
        }
        # return response
        # if user.is_admin:
        #     return RedirectResponse(url="/exhibitions")
        # elif user.is_admin is False:
        #     return RedirectResponse(url="/exhibitions")

    except Exception as e:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Ошибка при авторизации: {str(e)}"
        )

@app.get("/api/login_get")
async def login_get(
        external_id: int,
        session_id: str,
        full_name: str,
        department: str,
        position: str,
        response: Response,
        db: AsyncSession = Depends(get_db)
):
    """
    Авторизация пользователя из внешней системы

    Принимает данные в формате:
    {
        "id": "external_user_id",
        "fio": {"last_name": "Иванов", "first_name": "Иван", "middle_name": "Иванович"},
        "department": "Отдел продаж",
        "position": "Менеджер",
        "session_id": "session_token_123"
    }
    """

    try:
        # Извлекаем данные
        # external_id = int(user_data.get('id', None))
        # fio_data = user_data.get('fio', {})
        # department = user_data.get('department')
        # position = user_data.get('position')
        # session_id = user_data.get('session_id')

        if not external_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Не указан ID пользователя"
            )

        if not session_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Не указан session_id"
            )

        # Формируем ФИО
        # last_name = fio_data.get('last_name', '')
        # first_name = fio_data.get('first_name', '')
        # middle_name = fio_data.get('middle_name', '')
        # full_name = f"{last_name} {first_name} {middle_name}".strip()



        if not full_name:
            full_name = "Неизвестный пользователь"

        # Ищем пользователя в нашей БД по external_id
        result = await db.execute(
            select(User).where(User.id == external_id)
        )
        user = result.scalar_one_or_none()
        print(user)
        if user is not None:
            # Обновляем существующего пользователя
            user.full_name = full_name
            user.department = department
            user.position = position
            user.last_login = func.now()
        else:
            # Создаем нового пользователя
            user = User(
                id=external_id,
                full_name=full_name,
                department=department,
                position=position,
                is_admin=False,  # По умолчанию не админ
                last_login=func.now()
            )
            db.add(user)

        await db.commit()
        await db.refresh(user)

        redirect_url = f"https://exhibitions.emk.ru/api/docs"
        #  # Создаем RedirectResponse
        response = RedirectResponse(url=redirect_url)

        # Устанавливаем куки
        response.set_cookie(
            key="session_id",
            value=session_id,
            httponly=True,
            secure=False,  # В продакшене установите True
            samesite="lax",
            max_age=30 * 24 * 60 * 60  # 30 дней
        )

        response.set_cookie(
            key="user_id",
            value=str(external_id),
            httponly=True,
            secure=False,
            samesite="lax",
            max_age=30 * 24 * 60 * 60
        )

        # return {
        #     "message": "Успешная авторизация",
        #     "user": {
        #         "id": user.id,
        #         "full_name": user.full_name,
        #         "department": user.department,
        #         "position": user.position,
        #         "is_admin": user.is_admin
        #     }
        # }
        return response
        # if user.is_admin:
        #     return RedirectResponse(url="/exhibitions")
        # elif user.is_admin is False:
        #     return RedirectResponse(url="/exhibitions")

    except Exception as e:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Ошибка при авторизации: {str(e)}"
        )


@app.post("/api/logout")
async def logout(response: Response):
    """
    Выход из системы (очистка куки)
    """
    response.delete_cookie(key="session_id")
    response.delete_cookie(key="user_id")

    return {"message": "Успешный выход из системы"}

@app.get("/api/me")
async def get_current_user_info(
        session_id: Optional[str] = Cookie(None, alias="session_id"),
        user_id: Optional[int] = Cookie(None, alias="user_id"),
        db: AsyncSession = Depends(get_db)
):
    """
    Получение информации о текущем пользователе
    """
    if not user_id or not session_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Пользователь не авторизован"
        )

    result = await db.execute(
        select(User).where(User.id == user_id)
    )
    user = result.scalar_one_or_none()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Пользователь не найден"
        )

    # Проверяем, что пользователь активен
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Пользователь деактивирован"
        )

    return {
        "id": user.id,
        "external_id": user.external_id,
        "full_name": user.full_name,
        "department": user.department,
        "position": user.position,
        "is_admin": user.is_admin,
        "is_active": user.is_active,
        "last_login": user.last_login,
        "created_at": user.created_at
    }



@app.post("/api/ocr")
async def ocr_image(
    file: UploadFile = File(...)
):
    try:
        contents = await file.read()
        image = Image.open(io.BytesIO(contents))

        bw_img = image.convert('L')

        # edges = bw_img.filter(ImageFilter.FIND_EDGES)

        # min_noise = bw_img.filter(ImageFilter.MedianFilter())

        # enhancer = ImageEnhance.Contrast(min_noise)
        # # bw_img = min_noise.convert('L')

        # min_contrast = enhancer.enhance(2)

        res_img = bw_img

        text = pytesseract.image_to_string(res_img, lang='rus+eng')
        res_text = re.split(r'\n|\n\n|&', text)
        result = [item for item in res_text if item != ""]
        return result
    except Exception as e:
        return HTTPException(status_code=500, detail={"error ocr": str(e)})

@app.post("/api/ocr_new")
async def ocr_image(
    file: UploadFile = File(...)
):
    import re
    import io
    import numpy as np
    import cv2
    from PIL import Image, ImageEnhance, ImageFilter
    import pytesseract
    try:
        # contents = await file.read()
        contents = await file.read()
        image = Image.open(io.BytesIO(contents))

        # 1. Конвертация в grayscale
        gray = image.convert('L')

        # 2. Повышение контраста (умеренно)
        enhancer = ImageEnhance.Contrast(gray)
        gray = enhancer.enhance(1.8)

        # 3. Повышение резкости (Unsharp Mask)
        gray = gray.filter(ImageFilter.UnsharpMask(radius=1, percent=150, threshold=2))

        # 4. Медианный фильтр для удаления шума (размер 3)
        gray = gray.filter(ImageFilter.MedianFilter(size=3))

        # 5. Увеличение изображения, если оно маленькое (опционально)
        if gray.width < 1000 or gray.height < 1000:
            new_size = (gray.width * 2, gray.height * 2)
            gray = gray.resize(new_size, Image.Resampling.LANCZOS)

        # 6. Запускаем Tesseract с несколькими режимами PSM и выбираем лучший
        psms = [3, 4, 6, 11]  # 3 - авто, 4 - столбец, 6 - единый блок, 11 - разреженный текст
        best_text = ""
        max_lines = 0

        for psm in psms:
            config = f'--oem 3 --psm {psm}'  # без whitelist, чтобы не терять символы
            text = pytesseract.image_to_string(gray, lang='rus+eng', config=config)
            lines = [line.strip() for line in text.split('\n') if line.strip()]
            if len(lines) > max_lines:
                max_lines = len(lines)
                best_text = text
                print(psm, 'че лучше')

        # 7. Очистка результата (разбивка по строкам, удаление пустых)
        result = [line.strip() for line in best_text.split('\n') if line.strip()]

        def is_good_line(line: str) -> bool:
            # Убираем лишние пробелы
            s = line.strip()
            if not s:
                return False
            # Если строка состоит только из символов пунктуации/спецсимволов - отбрасываем
            # Подсчитаем количество буквенно-цифровых символов
            alnum_count = sum(c.isalnum() for c in s)
            # Общая длина
            total_len = len(s)
            # Если буквенно-цифровых символов меньше 30% - скорее всего мусор
            if total_len > 0 and alnum_count / total_len < 0.3:
                return False
            # Проверяем, есть ли в строке хотя бы одна последовательность букв длиной >=2 (слово)
            if not re.search(r'[a-zA-Zа-яА-ЯёЁ]{2,}', s):
                return False
            return True

        filtered_result = [line for line in result if is_good_line(line)]
        return result

        # return result
    except Exception as e:
        return HTTPException(status_code=500, detail={"error ocr": str(e)})


import asyncio
import aiohttp
from aiohttp import FormData
import time

URL = "http://exhibitions.kyberlox.ru/api/ocr_new"      # замените на ваш реальный URL
IMAGE_PATH = "говно1.jpg"                     # путь к изображению
NUM_REQUESTS = 10  
async def send_request(session, url, image_path, request_id):
    """
    Отправляет один multipart-запрос с файлом.
    Возвращает HTTP-статус или None в случае исключения.
    """
    try:
        # Формируем multipart/form-data с файлом
        data = FormData()
        # Важно: открываем файл заново для каждого запроса,
        # чтобы не было конфликтов с позицией чтения
        with open(image_path, 'rb') as f:
            file_content = f.read()

        data.add_field('file',
                       file_content,
                       filename='image.jpg',
                       content_type='image/jpeg')

        async with session.post(url, data=data) as response:
            status = response.status
            # Для отладки можно прочитать тело ответа
            # text = await response.text()
            print(f"[{request_id}] Статус: {status}")
            # if status != 200:
            #     print(f"[{request_id}] Ответ: {text[:200]}")
            return status
    except Exception as e:
        print(f"[{request_id}] Ошибка: {e}")
        return None

@app.post("/api/ocr_test")
async def test_ocr():
    start_time = time.time()

    # Увеличиваем лимит одновременных соединений
    connector = aiohttp.TCPConnector(limit=100)
    async with aiohttp.ClientSession(connector=connector) as session:
        tasks = []
        for i in range(1, NUM_REQUESTS + 1):
            tasks.append(send_request(session, URL, IMAGE_PATH, i))

        # Запускаем все задачи одновременно
        results = await asyncio.gather(*tasks, return_exceptions=True)

    end_time = time.time()

    # Подводим итоги
    success = sum(1 for r in results if r == 200)
    errors = sum(1 for r in results if r != 200 and r is not None)
    exceptions = sum(1 for r in results if r is None)

    print("\n========= РЕЗУЛЬТАТЫ =========")
    print(f"Всего запросов:      {NUM_REQUESTS}")
    print(f"Успешно (200):        {success}")
    print(f"Ошибки HTTP (не 200): {errors}")
    print(f"Исключения:           {exceptions}")
    print(f"Общее время:          {end_time - start_time:.2f} сек")
    print("===============================")

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info",
        access_log=True
    )
