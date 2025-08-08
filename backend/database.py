import os
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

# Configuración de base de datos
# Usar SQLite por defecto para facilitar el desarrollo
DATABASE_URL = os.getenv(
    "DATABASE_URL", 
    "sqlite:///./whatsapp_scheduler.db"  # SQLite local
)

# Para PostgreSQL, usar: 
# DATABASE_URL = "postgresql://usuario:password@localhost/whatsapp_scheduler"

# Crear engine
if DATABASE_URL.startswith("sqlite"):
    engine = create_engine(
        DATABASE_URL, 
        connect_args={"check_same_thread": False}  # Necesario para SQLite
    )
else:
    engine = create_engine(DATABASE_URL)

# Crear SessionLocal
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base para modelos
Base = declarative_base()

# Dependency para obtener DB session
def get_db():
    """
    Dependency que proporciona una sesión de base de datos.
    Se cierra automáticamente después de cada request.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Función para crear todas las tablas
def create_tables():
    """
    Crear todas las tablas en la base de datos.
    Se ejecuta al inicio de la aplicación.
    """
    Base.metadata.create_all(bind=engine)