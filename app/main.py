import uvicorn
from app.config import settings
from app.db.create_database import create_database_if_not_exists
from app.db.database import engine, Base
from fastapi import FastAPI
from app.api.endpoints import flats  # Импортируем наш новый роутер

app = FastAPI(title="Parsed Data API")

app.include_router(flats.router)  # Подключаем эндпоинты квартир

# create tables on startup (only for dev; for prod use alembic)
@app.on_event("startup")
async def on_startup():
    create_database_if_not_exists()

    # create tables if not exists
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

if __name__ == "__main__":
    uvicorn.run("app.main:app", host=settings.APP_HOST, port=settings.APP_PORT, reload=True)
