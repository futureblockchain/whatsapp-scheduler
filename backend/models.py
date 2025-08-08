from sqlalchemy import Column, Integer, String, DateTime, Boolean, Text
from sqlalchemy.sql import func
from database import Base
from datetime import datetime
from pydantic import BaseModel
from typing import Optional

# Modelo de SQLAlchemy para la tabla
class ScheduledMessage(Base):
    __tablename__ = "scheduled_messages"
    
    id = Column(Integer, primary_key=True, index=True)
    phone = Column(String(20), nullable=False, index=True)
    message = Column(Text, nullable=False)
    send_time = Column(DateTime, nullable=False, index=True)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    is_sent = Column(Boolean, default=False, index=True)
    sent_at = Column(DateTime, nullable=True)
    error_message = Column(Text, nullable=True)
    
    def __repr__(self):
        return f"<ScheduledMessage(id={self.id}, phone={self.phone}, send_time={self.send_time})>"

# Modelos Pydantic para request/response (Schemas)
class ScheduledMessageCreate(BaseModel):
    phone: str
    message: str
    send_time: datetime
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }

class ScheduledMessageResponse(BaseModel):
    id: int
    phone: str
    message: str
    send_time: datetime
    created_at: datetime
    updated_at: datetime
    is_sent: bool
    sent_at: Optional[datetime] = None
    error_message: Optional[str] = None
    
    class Config:
        from_attributes = True  # Para SQLAlchemy 2.0
        json_encoders = {
            datetime: lambda v: v.isoformat() if v else None
        }

class ScheduledMessageUpdate(BaseModel):
    phone: Optional[str] = None
    message: Optional[str] = None
    send_time: Optional[datetime] = None
    is_sent: Optional[bool] = None
    sent_at: Optional[datetime] = None
    error_message: Optional[str] = None