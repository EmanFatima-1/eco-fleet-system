import os
# pyrefly: ignore [missing-import]
from dotenv import load_dotenv

load_dotenv()


class Settings:
    PROJECT_TITLE: str = os.getenv(
        "PROJECT_TITLE", "Smart Eco-Fleet & Carbon Tracker"
    )
    PROJECT_VERSION: str = os.getenv("PROJECT_VERSION", "1.0.0")
    DATABASE_URL: str = os.getenv(
        "DATABASE_URL",
        "postgresql://postgres:YOUR_PASSWORD@localhost:5432/smart_task_db",
    )


settings = Settings()

PROJECT_TITLE = settings.PROJECT_TITLE
PROJECT_VERSION = settings.PROJECT_VERSION
DATABASE_URL = settings.DATABASE_URL
