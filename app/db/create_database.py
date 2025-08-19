import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
from app.config import settings

def create_database_if_not_exists():
    """
    Проверяет, есть ли база данных. Если нет — создаёт.
    """
    try:
        # Пробуем подключиться к целевой базе
        conn = psycopg2.connect(
            dbname=settings.POSTGRES_DB,
            user=settings.POSTGRES_USER,
            password=settings.POSTGRES_PASSWORD,
            host=settings.POSTGRES_HOST,
            port=settings.POSTGRES_PORT
        )
        conn.close()
        print(f"✅ База данных '{settings.POSTGRES_DB}' уже существует.")
    except psycopg2.OperationalError as e:
        if "does not exist" in str(e):
            print(f"⚠️  База '{settings.POSTGRES_DB}' не найдена. Создаём...")
            conn = psycopg2.connect(
                dbname=settings.POSTGRES_DB,
                user=settings.POSTGRES_USER,
                password=settings.POSTGRES_PASSWORD,
                host=settings.POSTGRES_HOST,
                port=settings.POSTGRES_PORT
            )
            conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
            cur = conn.cursor()
            cur.execute(f'CREATE DATABASE "{settings.POSTGRES_DB}"')
            cur.close()
            conn.close()
            print(f"✅ База '{settings.POSTGRES_DB}' успешно создана.")
        else:
            raise
