import os

class Settings:
    DATABASE_URL = os.getenv(
        "DATABASE_URL",
        "postgresql+psycopg2://postgres:12345@localhost:5432/weatherdb",
    )
    PAGE_SIZE_DEFAULT = 50
    PAGE_SIZE_MAX = 500

settings = Settings()
