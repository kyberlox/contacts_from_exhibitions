# routers/files.py
from fastapi import APIRouter, Depends, HTTPException, status, Query, UploadFile, File, BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from typing import List, Optional
from pathlib import Path

import aiofiles
import uuid
import os
from datetime import datetime

from models.database import get_db
from models.file import File as FileModel
from schemas.file import File as FileSchema
from schemas.file import FileCreate, FileShort, FileCreateRequest
from schemas.base import PaginationParams, PaginatedResponse

router = APIRouter(prefix="/files", tags=["Файлы"])



# Конфигурация
UPLOAD_DIR = Path("uploads")
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
ALLOWED_EXTENSIONS = {
    # Изображения
    ".jpg", ".jpeg", ".png", ".gif", ".webp", ".bmp", ".tiff", ".svg",
    # Документы
    ".pdf", ".doc", ".docx", ".xls", ".xlsx", ".ppt", ".pptx", ".txt", ".rtf",
    # Архивы
    ".zip", ".rar", ".7z",
    # Другие
    ".csv", ".json", ".xml"
}
MAX_FILE_SIZE = 100 * 1024 * 1024  # 100MB
CHUNK_SIZE = 1024 * 1024  # 1MB chunks

async def save_uploaded_file(
        upload_file: UploadFile,
        file_type: str = "general",
        custom_name: Optional[str] = None
) -> tuple[Path, str, str]:
    """
    Сохранение загруженного файла на диск
    Возвращает: (путь к файлу, уникальное имя файла, оригинальное имя)
    """
    # Проверяем расширение файла
    original_filename = upload_file.filename or "unnamed"
    file_extension = Path(original_filename).suffix.lower()

    if file_extension not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Недопустимый формат файла. Разрешены: {', '.join(sorted(ALLOWED_EXTENSIONS))}"
        )

    # Генерируем уникальное имя файла
    if custom_name:
        # Если указано кастомное имя, используем его (но добавляем расширение)
        base_name = Path(custom_name).stem
        unique_filename = f"{base_name}{file_extension}"
    else:
        # Генерируем уникальное имя на основе timestamp и uuid
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        file_uuid = str(uuid.uuid4())[:8]
        safe_name = Path(original_filename).stem.replace(" ", "_").replace(".", "_")
        unique_filename = f"{timestamp}_{file_uuid}_{safe_name}{file_extension}"

    # Создаем поддиректорию по типу файла если нужно
    type_dir = UPLOAD_DIR / file_type
    type_dir.mkdir(exist_ok=True)

    file_path = type_dir / unique_filename

    # Сохраняем файл чанками
    total_size = 0

    async with aiofiles.open(file_path, 'wb') as out_file:
        while True:
            chunk = await upload_file.read(CHUNK_SIZE)
            if not chunk:
                break

            total_size += len(chunk)
            if total_size > MAX_FILE_SIZE:
                # Удаляем частично загруженный файл
                if file_path.exists():
                    file_path.unlink()
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Файл слишком большой. Максимальный размер: {MAX_FILE_SIZE // 1024 // 1024}MB"
                )

            await out_file.write(chunk)

    return file_path, unique_filename, original_filename

async def create_file_record(
        db: AsyncSession,
        original_name: str,
        unique_name: str,
        file_path: Path,
        file_type: str = "general"
) -> FileModel:
    """Создание записи о файле в БД"""

    # Определяем формат файла
    file_extension = Path(original_name).suffix.lower().lstrip('.')
    if not file_extension:
        file_extension = "unknown"

    # Создаем URL (без домена)
    url_path = str(file_path.relative_to("uploads")).replace("\\", "/")
    url = f"/{url_path}"

    # Создаем запись в БД
    db_file = FileModel(
        name=original_name,
        format=file_extension,
        path=str(file_path),
        url=url,
        metadata={
            "original_name": original_name,
            "unique_name": unique_name,
            "type": file_type,
            "uploaded_at": datetime.now().isoformat()
        }
    )

    db.add(db_file)
    await db.flush()
    return db_file

@router.post("/upload", response_model=FileSchema, status_code=status.HTTP_201_CREATED)
async def upload_file(
        file: UploadFile = File(...),
        file_type: str = Query("general", description="Тип файла (например: general, image, document, business_card)"),
        custom_name: Optional[str] = Query(None, description="Кастомное имя файла (без расширения)"),
        db: AsyncSession = Depends(get_db)
):
    """
    Загрузка файла на сервер

    - **file**: Файл для загрузки
    - **file_type**: Тип файла для организации в директориях
    - **custom_name**: Опциональное кастомное имя файла
    """
    try:
        # Сохраняем файл на диск
        file_path, unique_name, original_name = await save_uploaded_file(
            upload_file=file,
            file_type=file_type,
            custom_name=custom_name
        )

        # Проверяем, нет ли уже файла с таким путем (уникальным именем)
        existing_file = await db.execute(
            select(FileModel).where(FileModel.path == str(file_path))
        )
        existing_file = existing_file.scalar_one_or_none()

        if existing_file:
            # Если файл уже существует, возвращаем существующую запись
            return existing_file

        # Создаем запись в БД
        db_file = await create_file_record(
            db=db,
            original_name=original_name,
            unique_name=unique_name,
            file_path=file_path,
            file_type=file_type
        )

        await db.commit()
        await db.refresh(db_file)

        return db_file

    except HTTPException:
        raise
    except Exception as e:
        # В случае ошибки откатываем транзакцию
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Ошибка при загрузке файла: {str(e)}"
        )

@router.post("/upload-multiple", response_model=List[FileSchema])
async def upload_multiple_files(
        files: List[UploadFile] = File(...),
        file_type: str = Query("general", description="Тип файлов"),
        db: AsyncSession = Depends(get_db)
):
    """
    Загрузка нескольких файлов одновременно
    """
    uploaded_files = []

    for upload_file in files:
        try:
            # Сохраняем каждый файл
            file_path, unique_name, original_name = await save_uploaded_file(
                upload_file=upload_file,
                file_type=file_type
            )

            # Проверяем на дубликат по пути
            existing_file = await db.execute(
                select(FileModel).where(FileModel.path == str(file_path))
            )
            existing_file = existing_file.scalar_one_or_none()

            if existing_file:
                uploaded_files.append(existing_file)
                continue

            # Создаем запись
            db_file = await create_file_record(
                db=db,
                original_name=original_name,
                unique_name=unique_name,
                file_path=file_path,
                file_type=file_type
            )

            uploaded_files.append(db_file)

        except Exception as e:
            # Пропускаем файл с ошибкой, продолжаем с остальными
            continue

    await db.commit()

    # Обновляем объекты из БД
    for file in uploaded_files:
        await db.refresh(file)

    return uploaded_files



@router.get("/", response_model=PaginatedResponse)
async def get_files(
        pagination: PaginationParams = Depends(),
        format_filter: Optional[str] = Query(None, description="Фильтр по формату файла"),
        db: AsyncSession = Depends(get_db)
):
    """Получение списка файлов"""
    query = select(FileModel)

    if format_filter:
        query = query.where(FileModel.format.ilike(f"%{format_filter}%"))

    # Сортировка по дате создания
    query = query.order_by(FileModel.created_at.desc())

    # Общее количество
    from sqlalchemy import func
    total_query = select(func.count()).select_from(query.subquery())
    total_result = await db.execute(total_query)
    total = total_result.scalar()

    # Пагинация
    query = query.offset(pagination.skip).limit(pagination.limit)

    result = await db.execute(query)
    files = result.scalars().all()

    items = [FileSchema.from_orm(file) for file in files]

    return PaginatedResponse(
        total=total,
        skip=pagination.skip,
        limit=pagination.limit,
        items=items
    )

@router.get("/{file_id}", response_model=FileSchema)
async def get_file(
        file_id: int,
        db: AsyncSession = Depends(get_db)
):
    """Получение информации о файле"""
    result = await db.execute(
        select(FileModel).where(FileModel.id == file_id)
    )
    file = result.scalar_one_or_none()

    if not file:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Файл не найден"
        )

    return file

@router.delete("/{file_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_file(
        file_id: int,
        db: AsyncSession = Depends(get_db)
):
    """Удаление файла"""
    result = await db.execute(
        select(FileModel).where(FileModel.id == file_id)
    )
    file = result.scalar_one_or_none()

    if not file:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Файл не найден"
        )

    # Удаляем файл с диска
    if Path(file.path).exists():
        Path(file.path).unlink()

    # Удаляем запись из БД
    await db.delete(file)
    await db.commit()

    return None