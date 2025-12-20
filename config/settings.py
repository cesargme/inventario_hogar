import os
from dotenv import load_dotenv

load_dotenv()

# App config
APP_NAME = "Inventario Alimentos"
APP_VERSION = "0.1.0"
ENVIRONMENT = os.getenv("ENVIRONMENT", "development")

# Auth
USERNAME = os.getenv("APP_USERNAME", "admin")
PASSWORD = os.getenv("APP_PASSWORD", "admin")

# OpenRouter API
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY", "")

# Database
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./inventario.db")

# SQLite Web UI
SQLITE_WEB_UI_PASSWORD = os.getenv("SQLITE_WEB_UI_PASSWORD", "admin")

# Lazy Loading Configuration
ITEMS_PER_PAGE = 5  # X = cantidad de items por página en lazy load
HISTORY_RECORDS_PER_ITEM = 10  # Y = cantidad de registros de historial por item
