import os
from pathlib import Path
from dotenv import load_dotenv


# Carga el .env local sin sobrescribir variables ya definidas en el entorno.
load_dotenv(Path(__file__).resolve().parents[1] / ".env")


class Config:
    DATABASE_URL = os.getenv("DATABASE_URL")
    SECRET_KEY = os.getenv("SECRET_KEY")

    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = "Lax"
    SESSION_COOKIE_SECURE = False