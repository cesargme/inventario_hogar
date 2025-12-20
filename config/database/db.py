import os
from sqlmodel import Session, SQLModel, create_engine
from dotenv import load_dotenv

# Cargar variables de entorno primero
load_dotenv()

# Database URL - PostgreSQL para production, SQLite opcional para desarrollo
USE_SQLITE = os.getenv("USE_SQLITE", "false").lower() == "true"

if USE_SQLITE:
    DATABASE_URL = "sqlite:///./inventario.db"
    connect_args = {"check_same_thread": False}
else:
    DATABASE_URL = os.getenv("DATABASE_URL")
    if not DATABASE_URL:
        raise ValueError("DATABASE_URL environment variable is required (or set USE_SQLITE=true for development)")
    connect_args = {}

engine = create_engine(
    DATABASE_URL,
    connect_args=connect_args,
    echo=False,
)


def create_db_and_tables():
    """Crea las tablas en la base de datos"""
    SQLModel.metadata.create_all(engine)


def get_session():
    """Dependency para obtener sesión de DB en FastAPI"""
    with Session(engine) as session:
        yield session


def init_db():
    """Inicializa la base de datos con datos seed"""
    from database.models import Section, User
    import bcrypt
    from dotenv import load_dotenv

    load_dotenv()

    create_db_and_tables()

    with Session(engine) as session:
        # Crear usuario si no existe
        username = os.getenv("APP_USERNAME", "admin")
        password = os.getenv("APP_PASSWORD", "admin")

        existing_user = session.query(User).filter(User.username == username).first()
        if not existing_user:
            password_hash = bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()
            user = User(username=username, password_hash=password_hash)
            session.add(user)
            session.commit()
            print(f"[OK] Usuario '{username}' creado")

        # Crear secciones por defecto si no existen
        default_sections = [
            {"name": "Refrigerador", "emoji": "🧊"},
            {"name": "Almacén 1", "emoji": "📦"},
            {"name": "Almacén 2", "emoji": "🏺"},
        ]

        for sec_data in default_sections:
            existing = (
                session.query(Section).filter(Section.name == sec_data["name"]).first()
            )
            if not existing:
                section = Section(**sec_data)
                session.add(section)

        session.commit()
        print("[OK] Secciones por defecto creadas")
