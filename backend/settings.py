import os
from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    """
    Configuración de la aplicación usando Pydantic Settings.
    Las variables se cargan automáticamente desde .env o variables de entorno.
    """
    
    # Database
    database_url: str = "sqlite:///./whatsapp_scheduler.db"
    
    # WhatsApp API (Meta Cloud API)
    whatsapp_access_token: Optional[str] = None
    whatsapp_phone_number_id: Optional[str] = None
    whatsapp_webhook_verify_token: Optional[str] = None
    
    # FastAPI
    app_name: str = "WhatsApp Scheduler API"
    app_version: str = "1.0.0"
    debug: bool = True
    
    # CORS
    allowed_origins: list = ["http://localhost:3000", "http://localhost:5173"]
    
    # Security
    secret_key: str = "your-super-secret-key-change-in-production"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    
    # Scheduler
    scheduler_timezone: str = "America/Mexico_City"
    check_interval_seconds: int = 30  # Revisar mensajes cada 30 segundos
    
    # Logging
    log_level: str = "INFO"
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False

# Instancia global de settings
settings = Settings()

# Función helper para verificar si estamos en modo desarrollo
def is_development() -> bool:
    return settings.debug

# Función helper para verificar si WhatsApp API está configurada
def is_whatsapp_configured() -> bool:
    return bool(settings.whatsapp_access_token and settings.whatsapp_phone_number_id)