from sqlalchemy import Column, Integer, String, DateTime, func
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class Flat(Base):
    """Модель квартиры (соответствует таблице flats в PostgreSQL)."""

    __tablename__ = "flats"

    id = Column(Integer, primary_key=True, index=True)
    url_card = Column(String, unique=True, nullable=False)  # Обязательное поле, уникальное
    title = Column(String)
    address = Column(String)
    discount_price = Column(String)  # Можно заменить на Numeric(10, 2)
    main_price = Column(String)
    old_price = Column(String)
    price_per_m2 = Column(String)
    year_of_construction = Column(String)  # Можно заменить на Integer
    posted_at = Column(DateTime(timezone=True), server_default=func.now())
    removed_at = Column(DateTime(timezone=True))
    last_updated = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())