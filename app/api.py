# from fastapi import APIRouter, Depends, HTTPException, Query
# from typing import List
# from sqlalchemy.ext.asyncio import AsyncSession
#
# from app.db import crud
# from app.db.database import get_db
# from app.schemas import ParsedDataCreate, ParsedDataRead, ParsedDataUpdate
#
# router = APIRouter(prefix="/parsed", tags=["parsed"])
#
# @router.post("/", response_model=ParsedDataRead, status_code=201)
# async def create_parsed(item: ParsedDataCreate, db: AsyncSession = Depends(get_db)):
#     created = await crud.create_parsed_data(db, source=item.source, data=item.data)
#     return created
#
# @router.get("/", response_model=List[ParsedDataRead])
# async def list_parsed(limit: int = Query(100, ge=1, le=1000), offset: int = 0, db: AsyncSession = Depends(get_db)):
#     return await crud.get_all_parsed(db, limit=limit, offset=offset)
#
# @router.get("/source/{source}", response_model=List[ParsedDataRead])
# async def list_by_source(source: str, limit: int = Query(100, ge=1, le=1000), offset: int = 0, db: AsyncSession = Depends(get_db)):
#     return await crud.get_parsed_by_source(db, source=source, limit=limit, offset=offset)
#
# @router.get("/{item_id}", response_model=ParsedDataRead)
# async def get_parsed(item_id: int, db: AsyncSession = Depends(get_db)):
#     item = await crud.get_parsed_by_id(db, item_id)
#     if not item:
#         raise HTTPException(status_code=404, detail="Not found")
#     return item
#
# @router.put("/{item_id}", response_model=ParsedDataRead)
# async def update_parsed(item_id: int, payload: ParsedDataUpdate, db: AsyncSession = Depends(get_db)):
#     updated = await crud.update_parsed_data(db, item_id, payload.data)
#     if not updated:
#         raise HTTPException(status_code=404, detail="Not found")
#     return updated
#
# @router.delete("/{item_id}", status_code=204)
# async def delete_parsed(item_id: int, db: AsyncSession = Depends(get_db)):
#     ok = await crud.delete_parsed_data(db, item_id)
#     if not ok:
#         raise HTTPException(status_code=404, detail="Not found")
#     return None
