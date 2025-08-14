from fastapi import APIRouter, Depends, HTTPException, Query
from typing import List
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.crud import (
    create_flat,
    get_all_flats,
    get_flat_by_id,
    get_flat_by_url,
    update_flat,
    delete_flat,
)
from app.db.database import get_db
from app.schemas import FlatCreate, FlatRead, FlatUpdate

router = APIRouter(prefix="/flats", tags=["flats"])

@router.post("/", response_model=FlatRead, status_code=201)
async def create_new_flat(flat: FlatCreate, db: AsyncSession = Depends(get_db)):
    """Добавить новую квартиру."""
    return await create_flat(db, flat.dict())

@router.get("/", response_model=List[FlatRead])
async def read_flats(
    limit: int = Query(100, ge=1, le=1000),
    offset: int = 0,
    db: AsyncSession = Depends(get_db)):
    """Получить список всех квартир."""
    return await get_all_flats(db, limit=limit, offset=offset)

@router.get("/{flat_id}", response_model=FlatRead)
async def read_flat(flat_id: int, db: AsyncSession = Depends(get_db)):
    """Получить квартиру по ID."""
    flat = await get_flat_by_id(db, flat_id)
    if not flat:
        raise HTTPException(status_code=404, detail="Flat not found")
    return flat

@router.get("/by-url/{url_card}", response_model=FlatRead)
async def read_flat_by_url(url_card: str, db: AsyncSession = Depends(get_db)):
    """Получить квартиру по URL."""
    flat = await get_flat_by_url(db, url_card)
    if not flat:
        raise HTTPException(status_code=404, detail="Flat not found")
    return flat

@router.put("/{flat_id}", response_model=FlatRead)
async def update_flat_data(
    flat_id: int,
    flat_data: FlatUpdate,
    db: AsyncSession = Depends(get_db)):
    """Обновить данные квартиры."""
    flat = await update_flat(db, flat_id, flat_data.dict(exclude_unset=True))
    if not flat:
        raise HTTPException(status_code=404, detail="Flat not found")
    return flat

@router.delete("/{flat_id}", status_code=204)
async def remove_flat(flat_id: int, db: AsyncSession = Depends(get_db)):
    """Пометить квартиру как удалённую."""
    ok = await delete_flat(db, flat_id)
    if not ok:
        raise HTTPException(status_code=404, detail="Flat not found")
    return None