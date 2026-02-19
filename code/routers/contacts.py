# routers/contacts.py
from fastapi import APIRouter, Depends, HTTPException, status, Query, UploadFile, File, Form, BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, or_, and_, text, desc, asc
from typing import List, Optional, Dict, Any
from datetime import datetime, date, timedelta
import json
import re
from pathlib import Path
import shutil

from models.database import get_db
from models.contact import Contact, ContactFileType, contact_file_association
from models.file import File as FileModel
from models.user import User
from models.exhibition import Exhibition
from schemas.contact import (
    ContactCreate,
    ContactUpdate,
    Contact as ContactSchema,
    ContactList,
    ContactWithExhibition,
    ContactFilter,
    ContactSearch,
    ContactImport,
    ContactBatchCreate,
    ContactExport,
    ContactStats,
    ContactDuplicateCheck,
    ContactDuplicateResponse,
    ContactAdminUpdate
)
from schemas.base import PaginationParams, PaginatedResponse

from services.auth import get_optional_user, require_admin, require_auth
from models.user import User
#from services.active_exhibition import get_current_exhibition



router = APIRouter(prefix="/contacts", tags=["Контаткты"])

# Конфигурация
UPLOAD_DIR = Path("uploads/contacts")
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
ALLOWED_FILE_EXTENSIONS = {
    ".jpg", ".jpeg", ".png", ".pdf", ".doc", ".docx", ".txt"
}
MAX_FILE_SIZE = 5 * 1024 * 1024  # 5MB
MAX_TOTAL_FILES_PER_CONTACT = 3  # Максимум 2 визитки + 1 документ

async def save_uploaded_file(
        file: UploadFile,
        contact_id: int,
        file_type: str = "business_card"
) -> FileModel:
    """Сохранение загруженного файла"""
    # Проверяем размер файла
    file.file.seek(0, 2)
    file_size = file.file.tell()
    file.file.seek(0)

    if file_size > MAX_FILE_SIZE:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Файл слишком большой. Максимальный размер: {MAX_FILE_SIZE // 1024 // 1024}MB"
        )

    # Проверяем расширение
    file_extension = Path(file.filename).suffix.lower()
    if file_extension not in ALLOWED_FILE_EXTENSIONS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Недопустимый формат файла. Разрешены: {', '.join(ALLOWED_FILE_EXTENSIONS)}"
        )

    # Генерируем уникальное имя
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    unique_filename = f"contact_{contact_id}_{file_type}_{timestamp}{file_extension}"
    file_path = UPLOAD_DIR / unique_filename

    # Сохраняем файл
    with open(file_path, "wb") as buffer:
        content = await file.read()
        buffer.write(content)

    # Создаем запись в БД
    db_file = FileModel(
        name=file.filename,
        format=file_extension.lstrip('.'),
        path=str(file_path),
        url=f"/uploads/contacts/{unique_filename}"
    )

    return db_file

async def check_contact_duplicate(
        contact_data: Dict[str, Any],
        db: AsyncSession,
        exclude_contact_id: Optional[int] = None
) -> List[str]:
    """Упрощенная проверка на дубликаты контакта"""
    duplicate_fields = []

    query = select(Contact)

    # Создаем список условий
    conditions = []

    # Проверяем по email
    if contact_data.get('email'):
        email = contact_data['email'].lower()
        email_condition = Contact.email == email
        conditions.append(email_condition)

    # Проверяем по телефону (простое сравнение, без очистки)
    if contact_data.get('phone_number'):
        phone_condition = Contact.phone_number == contact_data['phone_number']
        conditions.append(phone_condition)

    if not conditions:
        return duplicate_fields

    # Добавляем условие исключения текущего контакта
    if exclude_contact_id:
        query = query.where(Contact.id != exclude_contact_id)

    # Добавляем фильтр по выставке
    if contact_data.get('exhibition_id'):
        query = query.where(Contact.exhibition_id == contact_data['exhibition_id'])

    # Объединяем условия через OR
    query = query.where(or_(*conditions))

    result = await db.execute(query)
    existing_contact = result.scalar_one_or_none()

    if existing_contact:
        if contact_data.get('email') and existing_contact.email == contact_data['email'].lower():
            duplicate_fields.append('email')

        if contact_data.get('phone_number') and existing_contact.phone_number == contact_data['phone_number']:
            duplicate_fields.append('phone_number')

    return duplicate_fields

async def get_current_exhibition(
        db: AsyncSession = Depends(get_db)
) -> Optional[int]:
    """
    Dependency для получения текущего пользователя из куки
    """

    # Строим базовый запрос
    result = await db.execute(
            select(Exhibition).where(Exhibition.is_active == True)
        )
    exhibition_active = result.scalar_one_or_none()

    if exhibition_active is None:
        return None

    return exhibition_active.id

@router.get("/questionnaire")
def get_questionnaire():
    with open('./schemas/pattern.json', 'r') as f:
        if f:
            return json.load(f)
        else:
            return {}

@router.post("/", response_model=ContactWithExhibition, status_code=status.HTTP_201_CREATED)
async def create_contact(
        contact_data: ContactCreate,
        background_tasks: BackgroundTasks,
        current_user: Optional[User] = Depends(get_optional_user),
        db: AsyncSession = Depends(get_db),
        current_exhibition = Depends(get_current_exhibition)
):
    """Создание нового контакта"""

    # Подготавливаем данные
    contact_dict = contact_data.dict(exclude_none=True)

    if "exhibition_id" in contact_dict and contact_dict["exhibition_id"] is not None:
        # Проверяем существование выставки
        exhibition_result = await db.execute(
            select(Exhibition).where(Exhibition.id == contact_dict["exhibition_id"])
        )
        exhibition = exhibition_result.scalar_one_or_none()

        if not exhibition:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Выставка не найдена"
            )
        contact_dict["exhibition_id"]  = exhibition.id
    else:
        contact_dict["exhibition_id"] = current_exhibition #await get_current_exhibition(db)

    

    # Приводим email к нижнему регистру
    if 'email' in contact_dict and contact_dict['email']:
        contact_dict['email'] = contact_dict['email'].lower()

    # Добавляем автора, если пользователь авторизован
    if current_user:
        contact_dict['author_id'] = current_user.id
        print('author_id', current_user.id)

    # Создаем контакт
    db_contact = Contact(**contact_dict)
    db.add(db_contact)
    await db.flush()

    await db.commit()
    await db.refresh(db_contact)

    # Получаем полные данные для ответа
    result = await db.execute(
        select(Contact).where(Contact.id == db_contact.id)
    )

    contact = result.scalar_one()
    return contact.dict(exclude_none=True)

    # # Возвращаем данные вручную вместо from_orm()
    # return {
    #     "id": contact.id,
    #     "title": contact.title,
    #     "description": contact.description,
    #     "full_name": contact.full_name,
    #     "position": contact.position,
    #     "email": contact.email,
    #     "phone_number": contact.phone_number,
    #     "questionnaire": contact.questionnaire,
    #     "exhibition_id": contact.exhibition_id,
    #     "created_at": contact.created_at,
    #     "updated_at": contact.updated_at,
    #     "exhibition_id" : contact_dict["exhibition_id"]
    #     # "exhibition": {
    #     #     # "id": exhibition.id,
    #     #     # "title": exhibition.title,
    #     #     # "start_date": exhibition.start_date,
    #     #     # "end_date": exhibition.end_date,
    #     #     # "preview_file_id": exhibition.preview_file_id,
    #     # }
    # }

@router.post("/batch", response_model=List[ContactWithExhibition], status_code=status.HTTP_201_CREATED)
async def create_contacts_batch(
        batch_data: ContactBatchCreate,
        background_tasks: BackgroundTasks,
        db: AsyncSession = Depends(get_db)
):
    """Массовое создание контактов"""
    # Проверяем существование выставки
    exhibition_result = await db.execute(
        select(Exhibition).where(Exhibition.id == batch_data.exhibition_id)
    )
    exhibition = exhibition_result.scalar_one_or_none()

    if not exhibition:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Выставка не найдена"
        )

    created_contacts = []

    for contact_data in batch_data.contacts:
        # Подготавливаем данные
        contact_dict = contact_data.dict(exclude_none=True)
        contact_dict['exhibition_id'] = batch_data.exhibition_id

        # Проверяем на дубликаты
        duplicate_fields = await check_contact_duplicate(contact_dict, db)

        # Если есть дубликат, пропускаем или добавляем с пометкой
        if duplicate_fields:
            # Можно добавить логирование или пропустить контакт
            continue

        # Приводим email к нижнему регистру
        if 'email' in contact_dict and contact_dict['email']:
            contact_dict['email'] = contact_dict['email'].lower()

        # Создаем контакт
        db_contact = Contact(**contact_dict)
        db.add(db_contact)

    await db.commit()

    # Получаем созданные контакты
    # TODO: Улучшить получение созданных контактов

    return created_contacts

@router.get("/", response_model=PaginatedResponse, dependencies=[Depends(require_auth)])
async def get_contacts(
        pagination: PaginationParams = Depends(),
        exhibition_id: Optional[int] = Query(None, description="Фильтр по выставке"),
        search: Optional[str] = Query(None, description="Поиск по текстовым полям"),
        date_from: Optional[date] = Query(None, description="Дата создания от"),
        date_to: Optional[date] = Query(None, description="Дата создания до"),
        db: AsyncSession = Depends(get_db),
        current_user: User = Depends(get_optional_user)
):
    """Получение списка контактов с пагинацией и фильтрацией"""
    # Строим базовый запрос
    query = select(Contact)

    if not current_user.is_admin:
        if not current_user.id:
            raise HTTPException(status_code=403, detail="Доступ запрещён")
        query = query.where(Contact.author_id == current_user.id)

    # Применяем фильтры
    if exhibition_id:
        query = query.where(Contact.exhibition_id == exhibition_id)

    if search:
        search_pattern = f"%{search}%"
        query = query.where(
            or_(
                Contact.title.ilike(search_pattern),
                Contact.full_name.ilike(search_pattern),
                Contact.position.ilike(search_pattern),
                Contact.email.ilike(search_pattern),
                Contact.phone_number.ilike(search_pattern),
                Contact.description.ilike(search_pattern)
            )
        )

    if date_from:
        query = query.where(Contact.created_at >= date_from)

    if date_to:
        # Добавляем 1 день, чтобы включить весь день
        date_to_end = datetime.combine(date_to, datetime.max.time())
        query = query.where(Contact.created_at <= date_to_end)

    # Сортировка по дате создания (новые сначала)
    query = query.order_by(desc(Contact.created_at))

    # Общее количество
    total_query = select(func.count()).select_from(query.subquery())
    total_result = await db.execute(total_query)
    total = total_result.scalar()

    # Пагинация
    query = query.offset(pagination.skip).limit(pagination.limit)

    # Выполняем запрос
    result = await db.execute(query)
    contacts = result.scalars().all()

    # Преобразуем в схемы для списка
    items = [
        ContactList.from_orm(contact)
        for contact in contacts
    ]

    return PaginatedResponse(
        total=total,
        skip=pagination.skip,
        limit=pagination.limit,
        items=items
    )

@router.get("/{contact_id}", response_model=ContactWithExhibition)
async def get_contact(
        contact_id: int,
        db: AsyncSession = Depends(get_db)
):
    """Получение контакта по ID"""
    result = await db.execute(
        select(Contact).where(Contact.id == contact_id)
    )
    contact = result.scalar_one_or_none()

    if not contact:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Контакт не найден"
        )

    # Загружаем связанную выставку отдельно
    exhibition_result = await db.execute(
        select(Exhibition).where(Exhibition.id == contact.exhibition_id)
    )
    exhibition = exhibition_result.scalar_one_or_none()

    exhibition_data = None
    if exhibition:
        exhibition_data = {
            "id": exhibition.id,
            "title": exhibition.title,
            "start_date": exhibition.start_date,
            "end_date": exhibition.end_date,
            "preview_file_id": exhibition.preview_file_id,
        }

    # Возвращаем данные вручную
    return {
        "id": contact.id,
        "title": contact.title,
        "description": contact.description,
        "full_name": contact.full_name,
        "position": contact.position,
        "email": contact.email,
        "phone_number": contact.phone_number,
        "questionnaire": contact.questionnaire,
        "exhibition_id": contact.exhibition_id,
        "created_at": contact.created_at,
        "updated_at": contact.updated_at,
        "exhibition": exhibition_data,
    }

@router.put("/{contact_id}", response_model=ContactWithExhibition, dependencies=[Depends(require_auth)])
async def update_contact(
        contact_id: int,
        contact_data: ContactUpdate,
        db: AsyncSession = Depends(get_db),
        current_user: User = Depends(get_optional_user)
):
    """Обновление контакта"""
    result = await db.execute(
        select(Contact).where(Contact.id == contact_id)
    )
    contact = result.scalar_one_or_none()

    if not contact:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Контакт не найден"
        )

    if current_user.id != contact.author_id:
        if not current_user.is_admin:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="У вас нет прав на редактирование этого контакта"
            )

    # Проверяем на дубликаты (исключая текущий контакт)
    update_dict = contact_data.dict(exclude_unset=True)
    if update_dict:
        # Добавляем ID выставки для проверки в рамках той же выставки
        update_dict['exhibition_id'] = contact.exhibition_id
        duplicate_fields = await check_contact_duplicate(
            update_dict,
            db,
            exclude_contact_id=contact_id
        )

        if duplicate_fields:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Найден дубликат контакта по полям: {', '.join(duplicate_fields)}"
            )

    # Обновляем поля
    for field, value in contact_data.dict(exclude_unset=True).items():
        if value is not None:
            # Приводим email к нижнему регистру
            if field == 'email' and value:
                value = value.lower()
            setattr(contact, field, value)

    await db.commit()
    await db.refresh(contact)

    return contact

@router.put("/{contact_id}/admin", response_model=ContactWithExhibition, dependencies=[Depends(require_admin)])
async def admin_update_contact(
        contact_id: int,
        contact_data: ContactAdminUpdate,
        current_user: User = Depends(require_admin),
        db: AsyncSession = Depends(get_db)
):
    """Административное обновление контакта"""
    result = await db.execute(
        select(Contact).where(Contact.id == contact_id)
    )
    contact = result.scalar_one_or_none()

    if not contact:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Контакт не найден"
        )

    # Обновляем поля
    update_data = contact_data.dict(exclude_unset=True)

    # Если меняется статус валидации
    if 'is_validated' in update_data and update_data['is_validated'] != contact.is_validated:
        contact.is_validated = update_data['is_validated']
        contact.validated_by_id = current_user.id
        contact.validated_at = func.now()
        del update_data['is_validated']

    # Обновляем остальные поля
    for field, value in update_data.items():
        if value is not None:
            setattr(contact, field, value)

    await db.commit()
    await db.refresh(contact)

    return contact

@router.patch("/{contact_id}/validate", response_model=ContactWithExhibition, dependencies=[Depends(require_admin)])
async def validate_contact(
        contact_id: int,
        is_validated: bool = Query(..., description="Статус валидации"),
        notes: Optional[str] = Query(None, description="Заметки администратора"),
        current_user: User = Depends(require_admin),
        db: AsyncSession = Depends(get_db)
):
    """Валидация контакта администратором"""
    result = await db.execute(
        select(Contact).where(Contact.id == contact_id)
    )
    contact = result.scalar_one_or_none()

    if not contact:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Контакт не найден"
        )

    contact.is_validated = is_validated
    contact.validated_by_id = current_user.id
    contact.validated_at = func.now()

    if notes is not None:
        contact.notes = notes

    await db.commit()
    await db.refresh(contact)

    return contact

@router.delete("/{contact_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_contact(
        contact_id: int,
        db: AsyncSession = Depends(get_db)
):
    """Удаление контакта"""
    result = await db.execute(
        select(Contact).where(Contact.id == contact_id)
    )
    contact = result.scalar_one_or_none()

    if not contact:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Контакт не найден"
        )

    # TODO: Удалить связанные файлы с диска
    # Получаем файлы контакта
    files_result = await db.execute(
        select(ContactFileAssociation).where(
            ContactFileAssociation.contact_id == contact_id
        )
    )
    file_associations = files_result.scalars().all()

    # Удаляем файлы с диска
    for association in file_associations:
        file_result = await db.execute(
            select(FileModel).where(FileModel.id == association.file_id)
        )
        file = file_result.scalar_one_or_none()
        if file and Path(file.path).exists():
            Path(file.path).unlink()

    await db.delete(contact)
    await db.commit()

    return None

@router.post("/{contact_id}/files")
async def upload_contact_files(
        contact_id: int,
        background_tasks: BackgroundTasks,
        business_card_front: Optional[UploadFile] = File(None),
        business_card_back: Optional[UploadFile] = File(None),
        document: Optional[UploadFile] = File(None),
        db: AsyncSession = Depends(get_db)
):
    """Загрузка файлов для контакта (визитки и документы)"""
    # Проверяем существование контакта
    result = await db.execute(
        select(Contact).where(Contact.id == contact_id)
    )
    contact = result.scalar_one_or_none()

    if not contact:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Контакт не найден"
        )

    # Проверяем текущее количество файлов у контакта
    files_count_result = await db.execute(
        select(func.count()).where(contact_file_association.c.contact_id == contact_id)
    )
    current_files_count = files_count_result.scalar() or 0

    # Подготавливаем список файлов для загрузки
    files_to_upload = []
    file_types = []

    if business_card_front:
        files_to_upload.append(business_card_front)
        file_types.append(ContactFileType.BUSINESS_CARD_FRONT)

    if business_card_back:
        files_to_upload.append(business_card_back)
        file_types.append(ContactFileType.BUSINESS_CARD_BACK)

    if document:
        files_to_upload.append(document)
        file_types.append(ContactFileType.DOCUMENT)

    # Проверяем, не превысит ли загрузка лимит
    if current_files_count + len(files_to_upload) > MAX_TOTAL_FILES_PER_CONTACT:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Максимальное количество файлов на контакт: {MAX_TOTAL_FILES_PER_CONTACT}"
        )

    # Сохраняем файлы
    saved_files = []

    for i, (upload_file, file_type) in enumerate(zip(files_to_upload, file_types)):
        try:
            # Сохраняем файл
            db_file = await save_uploaded_file(upload_file, contact_id, file_type.value)
            db.add(db_file)
            await db.flush()

            # Создаем связь в ассоциативной таблице
            stmt = contact_file_association.insert().values(
                contact_id=contact_id,
                file_id=db_file.id,
                file_type=file_type.value
            )
            await db.execute(stmt)

            saved_files.append({
                "id": db_file.id,
                "name": db_file.name,
                "type": file_type.value,
                "url": db_file.url
            })

        except Exception as e:
            # Если возникла ошибка, откатываем транзакцию для этого файла
            await db.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Ошибка при сохранении файла {upload_file.filename}: {str(e)}"
            )

    await db.commit()

    return {
        "message": f"Успешно загружено {len(saved_files)} файлов",
        "files": saved_files,
        "contact_id": contact_id
    }

@router.delete("/{contact_id}/files/{file_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_contact_file(
        contact_id: int,
        file_id: int,
        db: AsyncSession = Depends(get_db)
):
    """Удаление файла контакта"""
    # Проверяем существование связи
    result = await db.execute(
        select(contact_file_association).where(
            (contact_file_association.c.contact_id == contact_id) &
            (contact_file_association.c.file_id == file_id)
        )
    )
    association = result.first()  # используем .first() вместо scalar_one_or_none()

    if not association:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Файл не найден у данного контакта"
        )

    # Получаем информацию о файле
    file_result = await db.execute(
        select(FileModel).where(FileModel.id == file_id)
    )
    file = file_result.scalar_one_or_none()

    # Удаляем файл с диска
    if file and Path(file.path).exists():
        Path(file.path).unlink()

    # Удаляем связь и файл из БД
    stmt = contact_file_association.delete().where(
        (contact_file_association.c.contact_id == contact_id) &
        (contact_file_association.c.file_id == file_id)
    )
    await db.execute(stmt)

    await db.commit()

    return None

@router.get("/{contact_id}/files")
async def get_contact_files(
        contact_id: int,
        db: AsyncSession = Depends(get_db)
):
    """Получение всех файлов контакта"""
    # Проверяем существование контакта
    contact_result = await db.execute(
        select(Contact).where(Contact.id == contact_id)
    )
    contact = contact_result.scalar_one_or_none()

    if not contact:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Контакт не найден"
        )

    try:
        # Простой двухшаговый подход:
        # 1. Сначала получаем все связи (ассоциации) для контакта
        associations_result = await db.execute(
            select(contact_file_association).where(
                contact_file_association.c.contact_id == contact_id
            )
        )
        associations = associations_result.all()

        # 2. Для каждой связи получаем файл
        files = []
        for assoc in associations:
            # assoc - это RowProxy объект с доступом к колонкам через индекс или имя
            file_id = assoc.file_id
            file_type = assoc.file_type

            # Получаем файл
            file_result = await db.execute(
                select(FileModel).where(FileModel.id == file_id)
            )
            file = file_result.scalar_one_or_none()

            if file:
                files.append({
                    "file_id": file.id,
                    "name": file.name,
                    "type": file_type,
                    "url": file.url,
                    "format": file.format,
                    "created_at": file.created_at
                })

        return {
            "contact_id": contact_id,
            "total_files": len(files),
            "files": files
        }

    except Exception as e:
        print(f"Ошибка в get_contact_files: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Ошибка при получении файлов: {str(e)}"
        )

@router.get("/stats/overview", response_model=ContactStats)
async def get_contacts_stats(
        exhibition_id: Optional[int] = Query(None, description="Фильтр по выставке"),
        db: AsyncSession = Depends(get_db)
):
    """Получение статистики по контактам"""
    from sqlalchemy import func, extract

    # Общее количество контактов
    total_query = select(func.count(Contact.id))
    if exhibition_id:
        total_query = total_query.where(Contact.exhibition_id == exhibition_id)

    total_result = await db.execute(total_query)
    total_contacts = total_result.scalar() or 0

    # Контакты по выставкам
    exhibition_stats_query = select(
        Exhibition.title,
        func.count(Contact.id).label('count')
    ).join(
        Contact,
        Exhibition.id == Contact.exhibition_id
    ).group_by(Exhibition.id, Exhibition.title)

    if exhibition_id:
        exhibition_stats_query = exhibition_stats_query.where(Exhibition.id == exhibition_id)

    exhibition_stats_result = await db.execute(exhibition_stats_query)
    contacts_by_exhibition = {
        row.title: row.count
        for row in exhibition_stats_result.all()
    }

    # Контакты по должностям (топ-10)
    position_stats_query = select(
        Contact.position,
        func.count(Contact.id).label('count')
    ).where(
        Contact.position.isnot(None)
    ).group_by(Contact.position).order_by(desc('count')).limit(10)

    if exhibition_id:
        position_stats_query = position_stats_query.where(Contact.exhibition_id == exhibition_id)

    position_stats_result = await db.execute(position_stats_query)
    contacts_by_position = {
        row.position: row.count
        for row in position_stats_result.all()
    }

    # Контакты за последнюю неделю
    week_ago = datetime.now() - timedelta(days=7)
    last_week_query = select(func.count(Contact.id)).where(Contact.created_at >= week_ago)
    if exhibition_id:
        last_week_query = last_week_query.where(Contact.exhibition_id == exhibition_id)

    last_week_result = await db.execute(last_week_query)
    contacts_last_week = last_week_result.scalar() or 0

    # Контакты за сегодня
    today_start = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
    today_query = select(func.count(Contact.id)).where(Contact.created_at >= today_start)
    if exhibition_id:
        today_query = today_query.where(Contact.exhibition_id == exhibition_id)

    today_result = await db.execute(today_query)
    contacts_today = today_result.scalar() or 0

    return ContactStats(
        total_contacts=total_contacts,
        contacts_by_exhibition=contacts_by_exhibition,
        contacts_by_position=contacts_by_position,
        contacts_last_week=contacts_last_week,
        contacts_today=contacts_today
    )