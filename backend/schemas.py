from pydantic import BaseModel, Field, validator
from datetime import datetime, timezone
from typing import Optional
import re

class ScheduledMessageBase(BaseModel):
    """Schema base para mensajes programados"""
    phone: str = Field(..., min_length=10, max_length=20, description="Número de WhatsApp")
    message: str = Field(..., min_length=1, max_length=4096, description="Mensaje a enviar")
    
    @validator('phone')
    def validate_phone(cls, v):
        # Limpiar el número (quitar espacios, guiones, etc.)
        clean_phone = re.sub(r'[^\d+]', '', v)
        
        # Validar formato E.164 internacional: + seguido de 7-15 dígitos
        if not re.match(r'^\+[1-9]\d{7,14}$', clean_phone):
            raise ValueError('Formato inválido. Use un número internacional válido con prefijo (ej: +1555612891, +525512345678)')
        
        return clean_phone

class ScheduledMessageCreate(ScheduledMessageBase):
    """Schema para crear un mensaje programado"""
    send_time: datetime = Field(..., description="Fecha y hora de envío")
    
    @validator('send_time')
    def validate_send_time(cls, v):
        # Asegurar que ambas fechas sean timezone-aware
        now = datetime.now(timezone.utc)
        
        # Si v no tiene timezone, asumimos UTC
        if v.tzinfo is None:
            v = v.replace(tzinfo=timezone.utc)
        
        if v <= now:
            raise ValueError('La fecha de envío debe ser en el futuro')
        return v

class ScheduledMessageUpdate(BaseModel):
    """Schema para actualizar un mensaje programado"""
    phone: Optional[str] = None
    message: Optional[str] = None
    send_time: Optional[datetime] = None
    
    @validator('phone')
    def validate_phone(cls, v):
        if v is not None:
            clean_phone = re.sub(r'[^\d+]', '', v)
            if not re.match(r'^\+[1-9]\d{7,14}$', clean_phone):
                raise ValueError('Formato inválido. Use un número internacional válido con prefijo')
        return v
    
    @validator('send_time')
    def validate_send_time(cls, v):
        if v is not None:
            now = datetime.now(timezone.utc)
            if v.tzinfo is None:
                v = v.replace(tzinfo=timezone.utc)
            if v <= now:
                raise ValueError('La fecha de envío debe ser en el futuro')
        return v

class ScheduledMessageResponse(ScheduledMessageBase):
    """Schema para respuesta de mensaje programado"""
    id: int
    send_time: datetime
    created_at: datetime
    updated_at: datetime
    is_sent: bool = False
    sent_at: Optional[datetime] = None
    error_message: Optional[str] = None
    
    class Config:
        from_attributes = True

class MessageSendRequest(BaseModel):
    """Schema para envío inmediato de mensaje (testing)"""
    phone: str = Field(..., min_length=10, max_length=20)
    message: str = Field(..., min_length=1, max_length=4096)
    
    @validator('phone')
    def validate_phone(cls, v):
        clean_phone = re.sub(r'[^\d+]', '', v)
        if not re.match(r'^\+[1-9]\d{7,14}$', clean_phone):
            raise ValueError('Formato inválido. Use un número internacional válido con prefijo')
        return clean_phone

class MessageSendResponse(BaseModel):
    """Schema para respuesta de envío de mensaje"""
    success: bool
    message_id: Optional[str] = None
    status: str
    timestamp: datetime
    error: Optional[str] = None

class MessageListResponse(BaseModel):
    """Schema para lista paginada de mensajes"""
    messages: list[ScheduledMessageResponse]
    total: int
    page: int = 1
    per_page: int = 50
    
class APIResponse(BaseModel):
    """Schema genérico para respuestas de API"""
    success: bool
    message: str
    data: Optional[dict] = None