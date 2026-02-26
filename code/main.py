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
app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")

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

        redirect_url = f"http://exhibitions.emk.org.ru/api/docs"
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



# @app.post("/api/ocr")
# async def ocr_image(
#     file: UploadFile = File(...)
# ):
#     import io
#     import numpy as np
#     import cv2
#     from PIL import Image, ImageEnhance, ImageFilter
#     import pytesseract
#     try:
#         contents = await file.read()
#         image = Image.open(io.BytesIO(contents))

#         bw_img = image.convert('L')

#         # edges = bw_img.filter(ImageFilter.FIND_EDGES)

#         min_noise = bw_img.filter(ImageFilter.MedianFilter())

#         enhancer = ImageEnhance.Contrast(min_noise)
#         # bw_img = min_noise.convert('L')

#         min_contrast = enhancer.enhance(2)

#         res_img = min_contrast

#         text = pytesseract.image_to_string(res_img, lang='rus+eng')
#         res_text = re.split(r'\n|\n\n|&', text)
#         result = [item for item in res_text if item != ""]
#         return result
#     except Exception as e:
#         return HTTPException(status_code=500, detail={"error ocr": str(e)})
@app.post("/api/ocr")
async def ocr_image(
    file: UploadFile = File(...)
):
    import io
    import numpy as np
    import cv2
    from PIL import Image, ImageEnhance, ImageFilter
    import pytesseract
    try:
        contents = await file.read()
        # Чтение изображения с помощью OpenCV
        nparr = np.frombuffer(contents, np.uint8)
        img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        if img is None:
            return ""  # Ошибка загрузки

        # 1. Увеличение резкости (unsharp mask)
        def unsharp_mask(image, kernel_size=(5,5), sigma=1.0, amount=1.5, threshold=0):
            blurred = cv2.GaussianBlur(image, kernel_size, sigma)
            sharpened = float(amount + 1) * image - float(amount) * blurred
            sharpened = np.maximum(sharpened, np.zeros(sharpened.shape))
            sharpened = np.minimum(sharpened, 255 * np.ones(sharpened.shape))
            sharpened = sharpened.round().astype(np.uint8)
            if threshold > 0:
                low_contrast_mask = np.absolute(image - blurred) < threshold
                np.copyto(sharpened, image, where=low_contrast_mask)
            return sharpened

        img = unsharp_mask(img)

        # 2. Преобразование в оттенки серого
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

        # 3. Удаление шума (медианный фильтр)
        gray = cv2.medianBlur(gray, 3)

        # 4. Бинаризация (адаптивный порог или Отсу)
        # Если текст темный на светлом фоне, то инвертируем
        # Для визиток обычно тёмный текст на светлом фоне
        # Используем адаптивный порог, чтобы учесть неравномерность освещения
        binary = cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
                                    cv2.THRESH_BINARY, 15, 10)
        # Альтернатива: метод Отсу, если фон равномерный
        # _, binary = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)

        # 5. Увеличение размера, если текст мелкий (например, в 2 раза)
        height, width = binary.shape
        if height < 1000 or width < 1000:  # если маленькое разрешение
            scale = 2
            new_size = (width * scale, height * scale)
            binary = cv2.resize(binary, new_size, interpolation=cv2.INTER_CUBIC)

        # 6. Удаление мелких шумов (морфологическая операция)
        kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (2, 2))
        binary = cv2.morphologyEx(binary, cv2.MORPH_CLOSE, kernel)  # закрытие дыр
        binary = cv2.morphologyEx(binary, cv2.MORPH_OPEN, kernel)   # удаление точек

        # 7. Коррекция наклона (deskew)
        coords = np.column_stack(np.where(binary > 0))
        if len(coords) > 0:
            angle = cv2.minAreaRect(coords)[-1]
            if angle < -45:
                angle = -(90 + angle)
            else:
                angle = -angle
            if abs(angle) > 0.5:
                (h, w) = binary.shape[:2]
                center = (w // 2, h // 2)
                M = cv2.getRotationMatrix2D(center, angle, 1.0)
                binary = cv2.warpAffine(binary, M, (w, h), flags=cv2.INTER_CUBIC,
                                        borderMode=cv2.BORDER_REPLICATE)

        # 8. Опционально: обрезка по краям, удаление лишних линий
        # Например, можно удалить рамки с помощью морфологии

        # 9. Конвертируем обратно в PIL для pytesseract (или можно напрямую использовать cv2 с pytesseract)
        pil_img = Image.fromarray(binary)

        # 10. Запуск Tesseract с оптимальными параметрами для визитки
        custom_config = r'--oem 3 --psm 6 -c tessedit_char_whitelist="ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789@.-_ "'
        text = pytesseract.image_to_string(pil_img, lang='rus+eng', config=custom_config)

        return text.strip()

        # return result
    except Exception as e:
        return HTTPException(status_code=500, detail={"error ocr": str(e)})

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info",
        access_log=True
    )
