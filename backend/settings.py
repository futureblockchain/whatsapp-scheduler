import os
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

class Settings:
    """Configuración de la aplicación"""
    
    # Información de la aplicación
    app_name: str = "WhatsApp Scheduler API"
    app_version: str = "1.0.0"
    debug: bool = os.getenv("DEBUG", "false").lower() == "true"
    
    # CORS
    allowed_origins: list = [
        "http://localhost:3000",  # React dev server
        "http://localhost:5173",  # Vite dev server
        "http://127.0.0.1:3000",
        "http://127.0.0.1:5173",
    ]
    
    # Base de datos
    database_url: str = os.getenv(
        "DATABASE_URL", 
        "sqlite:///./whatsapp_scheduler.db"
    )
    
    # WhatsApp API configuración
    whatsapp_api_base: str = "https://graph.facebook.com"
    whatsapp_api_version: str = "v20.0"
    whatsapp_access_token: str = os.getenv("WHATSAPP_ACCESS_TOKEN", "")
    whatsapp_phone_number_id: str = os.getenv("WHATSAPP_PHONE_NUMBER_ID", "")
    
    # Scheduler configuración
    scheduler_timezone: str = os.getenv("SCHEDULER_TIMEZONE", "UTC")
    
    # Logging
    log_level: str = os.getenv("LOG_LEVEL", "INFO")
    log_file: str = os.getenv("LOG_FILE", "whatsapp_scheduler.log")

# Instancia global de configuración
settings = Settings()