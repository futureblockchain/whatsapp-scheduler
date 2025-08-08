from pydantic import BaseModel, Field, validator
from datetime import datetime
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
        
        # Validar formato básico
        if not re.match(r'^(\+?52)?[0-9]{10}$', clean_phone.replace('+', '')):
            raise ValueError('Número de teléfono debe tener 10 dígitos (formato México)')
        
        return clean_phone

class ScheduledMessageCreate(ScheduledMessageBase):
    """Schema para crear un mensaje programado"""
    send_time: datetime = Field(..., description="Fecha y hora de envío")
    
    @validator('send_time')
    def validate_send_time(cls, v):
        if v <= datetime.now():
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
            if not re.match(r'^(\+?52)?[0-9]{10}$', clean_phone.replace('+', '')):
                raise ValueError('Número de teléfono debe tener 10 dígitos (formato México)')
        return v
    
    @validator('send_time')
    def validate_send_time(cls, v):
        if v is not None and v <= datetime.now():
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
        if not re.match(r'^(\+?52)?[0-9]{10}$', clean_phone.replace('+', '')):
            raise ValueError('Número de teléfono debe tener 10 dígitos (formato México)')
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