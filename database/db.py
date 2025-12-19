import os
from sqlmodel import Session, SQLModel, create_engine

# Database URL - usar /data para Railway volume sharing
DB_PATH = os.getenv("DB_PATH", "./inventario.db")
DATABASE_URL = f"sqlite:///{DB_PATH}"

# Create engine
engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False},  # Necesario para SQLite
    echo=False,  # Desactivar logs SQL para evitar problemas de encoding
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
