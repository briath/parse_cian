from sqlalchemy import select, update, delete, func
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.models import Flat

async def create_flat(db: AsyncSession, flat_data: dict):
    """Создать новую запись о квартире."""
    flat = Flat(**flat_data)
    db.add(flat)
    await db.commit()
    await db.refresh(flat)
    return flat

async def get_all_flats(db: AsyncSession, limit: int = 100, offset: int = 0):
    """Получить все квартиры с пагинацией."""
    result = await db.execute(select(Flat).where(Flat.removed_at.is_(None)).offset(offset).limit(limit))
    return result.scalars().all()

async def get_flat_by_id(db: AsyncSession, flat_id: int):
    """Получить квартиру по ID (только если не удалена)."""
    result = await db.execute(select(Flat).where(Flat.id == flat_id, Flat.removed_at.is_(None)))
    return result.scalar_one_or_none()

async def get_flat_by_url(db: AsyncSession, url_card: str):
    """Получить квартиру по URL (только если не удалена)."""
    result = await db.execute(select(Flat).where(Flat.url_card == url_card, Flat.removed_at.is_(None)))
    return result.scalar_one_or_none()

async def update_flat(db: AsyncSession, flat_id: int, flat_data: dict):
    """Обновить данные квартиры."""
    stmt = (
        update(Flat)
        .where(Flat.id == flat_id)
        .values(**flat_data)
    )
    await db.execute(stmt)
    await db.commit()
    return await get_flat_by_id(db, flat_id)

async def delete_flat(db: AsyncSession, flat_id: int):
    """Пометить квартиру как удалённую (soft delete)."""
    stmt = (
        update(Flat)
        .where(Flat.id == flat_id)
        .values(removed_at=func.now())
    )
    await db.execute(stmt)
    await db.commit()
    return True