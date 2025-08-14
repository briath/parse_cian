from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    POSTGRES_USER: str = "postgres"
    POSTGRES_PASSWORD: str = "KpSs2uR2"
    POSTGRES_HOST: str = "localhost"
    POSTGRES_PORT: int = 5432
    POSTGRES_DB: str = "postgres"
    APP_HOST: str = "0.0.0.0"
    APP_PORT: int = 8000
    PGADMIN_DEFAULT_EMAIL = "admin@example.com"
    PGADMIN_DEFAULT_PASSWORD = "PgAdminSecurePass456!"
    PGADMIN_PORT = 5050

    class Config:
        env_file = ".env"

settings = Settings()

