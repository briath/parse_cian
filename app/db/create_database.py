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
            dbname=settings.DB_NAME,
            user=settings.DB_USER,
            password=settings.DB_PASSWORD,
            host=settings.DB_HOST,
            port=settings.DB_PORT
        )
        conn.close()
        print(f"✅ База данных '{settings.DB_NAME}' уже существует.")
    except psycopg2.OperationalError as e:
        if "does not exist" in str(e):
            print(f"⚠️  База '{settings.DB_NAME}' не найдена. Создаём...")
            conn = psycopg2.connect(
                dbname="postgres",  # подключаемся к системной БД
                user=settings.DB_USER,
                password=settings.DB_PASSWORD,
                host=settings.DB_HOST,
                port=settings.DB_PORT
            )
            conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
            cur = conn.cursor()
            cur.execute(f'CREATE DATABASE "{settings.DB_NAME}"')
            cur.close()
            conn.close()
            print(f"✅ База '{settings.DB_NAME}' успешно создана.")
        else:
            raise
