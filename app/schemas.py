from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class FlatBase(BaseModel):
    url_card: str
    title: Optional[str] = None
    address: Optional[str] = None
    discount_price: Optional[str] = None
    main_price: Optional[str] = None
    old_price: Optional[str] = None
    price_per_m2: Optional[str] = None
    year_of_construction: Optional[str] = None

class FlatCreate(FlatBase):
    pass

class FlatUpdate(BaseModel):
    title: Optional[str] = None
    address: Optional[str] = None
    discount_price: Optional[str] = None
    main_price: Optional[str] = None
    old_price: Optional[str] = None
    price_per_m2: Optional[str] = None
    year_of_construction: Optional[str] = None

class FlatRead(FlatBase):
    id: int
    posted_at: datetime
    removed_at: Optional[datetime] = None
    last_updated: datetime

    class Config:
        orm_mode = True