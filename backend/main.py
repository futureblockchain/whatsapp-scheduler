from fastapi import FastAPI, Depends, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, desc
from datetime import datetime
from typing import List, Optional
import uvicorn

from database import get_db, create_tables
from models import ScheduledMessage
from schemas import (
    ScheduledMessageCreate,
    ScheduledMessageUpdate,
    ScheduledMessageResponse,
    MessageSendRequest,
    MessageSendResponse,
    MessageListResponse,
    APIResponse
)
from whatsapp_service import whatsapp_service
from scheduler import scheduler_service
from settings import settings

# Crear instancia de FastAPI
app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description="API para programar mensajes de WhatsApp",
    debug=settings.debug
)

# Configurar CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
async def startup_event():
    """Eventos al iniciar la aplicación"""
    print("🚀 Iniciando WhatsApp Scheduler API...")
    
    # Crear tablas
    create_tables()
    print("📊 Base de datos inicializada")
    
    # Iniciar scheduler
    scheduler_service.start()

@app.on_event("shutdown")
async def shutdown_event():
    """Eventos al cerrar la aplicación"""
    print("🛑 Cerrando WhatsApp Scheduler API...")
    scheduler_service.stop()

# ============================================================================
# ENDPOINTS PRINCIPALES
# ============================================================================

@app.get("/", response_model=APIResponse)
async def root():
    """Endpoint de prueba"""
    return APIResponse(
        success=True,
        message=f"WhatsApp Scheduler API v{settings.app_version} está funcionando",
        data={
            "whatsapp_configured": bool(settings.whatsapp_access_token),
            "scheduler_running": scheduler_service.is_running,
            "timezone": settings.scheduler_timezone
        }
    )

@app.post("/api/schedule", response_model=ScheduledMessageResponse)
async def create_scheduled_message(
    message: ScheduledMessageCreate,
    db: Session = Depends(get_db)
):
    """Crear un nuevo mensaje programado"""
    
    # Crear mensaje en la base de datos
    db_message = ScheduledMessage(
        phone=message.phone,
        message=message.message,
        send_time=message.send_time
    )
    
    db.add(db_message)
    db.commit()
    db.refresh(db_message)
    
    # Programar el envío
    await scheduler_service.schedule_message(db_message.id, message.send_time)
    
    return db_message

@app.get("/api/scheduled", response_model=MessageListResponse)
async def get_scheduled_messages(
    page: int = Query(1, ge=1, description="Página"),
    per_page: int = Query(50, ge=1, le=100, description="Mensajes por página"),
    status: Optional[str] = Query(None, description="Filtrar por estado: pending, sent, failed"),
    phone: Optional[str] = Query(None, description="Filtrar por número de teléfono"),
    db: Session = Depends(get_db)
):
    """Obtener lista de mensajes programados con filtros y paginación"""
    
    # Base query
    query = db.query(ScheduledMessage)
    
    # Aplicar filtros
    if status:
        if status == "pending":
            query = query.filter(and_(
                ScheduledMessage.is_sent == False,
                ScheduledMessage.send_time > datetime.now()
            ))
        elif status == "sent":
            query = query.filter(ScheduledMessage.is_sent == True)
        elif status == "failed":
            query = query.filter(and_(
                ScheduledMessage.is_sent == False,
                ScheduledMessage.error_message.isnot(None)
            ))
    
    if phone:
        query = query.filter(ScheduledMessage.phone.contains(phone))
    
    # Obtener total
    total = query.count()
    
    # Aplicar paginación y ordenamiento
    messages = query.order_by(desc(ScheduledMessage.created_at))\
                   .offset((page - 1) * per_page)\
                   .limit(per_page)\
                   .all()
    
    return MessageListResponse(
        messages=messages,
        total=total,
        page=page,
        per_page=per_page
    )

@app.get("/api/scheduled/{message_id}", response_model=ScheduledMessageResponse)
async def get_scheduled_message(message_id: int, db: Session = Depends(get_db)):
    """Obtener un mensaje programado específico"""
    
    message = db.query(ScheduledMessage).filter(ScheduledMessage.id == message_id).first()
    
    if not message:
        raise HTTPException(status_code=404, detail="Mensaje no encontrado")
    
    return message

@app.put("/api/scheduled/{message_id}", response_model=ScheduledMessageResponse)
async def update_scheduled_message(
    message_id: int,
    message_update: ScheduledMessageUpdate,
    db: Session = Depends(get_db)
):
    """Actualizar un mensaje programado"""
    
    message = db.query(ScheduledMessage).filter(ScheduledMessage.id == message_id).first()
    
    if not message:
        raise HTTPException(status_code=404, detail="Mensaje no encontrado")
    
    if message.is_sent:
        raise HTTPException(status_code=400, detail="No se puede editar un mensaje ya enviado")
    
    # Actualizar campos
    update_data = message_update.dict(exclude_unset=True)
    
    for field, value in update_data.items():
        setattr(message, field, value)
    
    message.updated_at = datetime.now()
    
    db.commit()
    db.refresh(message)
    
    # Re-programar si cambió la fecha
    if message_update.send_time:
        await scheduler_service.schedule_message(message.id, message_update.send_time)
    
    return message

@app.delete("/api/scheduled/{message_id}", response_model=APIResponse)
async def delete_scheduled_message(message_id: int, db: Session = Depends(get_db)):
    """Eliminar un mensaje programado"""
    
    message = db.query(ScheduledMessage).filter(ScheduledMessage.id == message_id).first()
    
    if not message:
        raise HTTPException(status_code=404, detail="Mensaje no encontrado")
    
    # Cancelar el job programado
    await scheduler_service.cancel_message(message_id)
    
    # Eliminar de la base de datos
    db.delete(message)
    db.commit()
    
    return APIResponse(
        success=True,
        message=f"Mensaje {message_id} eliminado correctamente"
    )

# ============================================================================
# ENDPOINTS DE TESTING Y UTILIDADES
# ============================================================================

@app.post("/api/send-now", response_model=MessageSendResponse)
async def send_message_now(message: MessageSendRequest):
    """Enviar un mensaje inmediatamente (para testing)"""
    
    result = await whatsapp_service.send_message(
        phone=message.phone,
        message=message.message
    )
    
    return MessageSendResponse(
        success=result.get('success', False),
        message_id=result.get('message_id'),
        status=result.get('status', 'unknown'),
        timestamp=datetime.now(),
        error=result.get('error')
    )

@app.get("/api/stats")
async def get_stats(db: Session = Depends(get_db)):
    """Obtener estadísticas del sistema"""
    
    total_messages = db.query(ScheduledMessage).count()
    sent_messages = db.query(ScheduledMessage).filter(ScheduledMessage.is_sent == True).count()
    pending_messages = db.query(ScheduledMessage).filter(
        and_(
            ScheduledMessage.is_sent == False,
            ScheduledMessage.send_time > datetime.now()
        )
    ).count()
    failed_messages = db.query(ScheduledMessage).filter(
        and_(
            ScheduledMessage.is_sent == False,
            ScheduledMessage.error_message.isnot(None)
        )
    ).count()
    
    return {
        "total_messages": total_messages,
        "sent_messages": sent_messages,
        "pending_messages": pending_messages,
        "failed_messages": failed_messages,
        "success_rate": round((sent_messages / total_messages * 100), 2) if total_messages > 0 else 0,
        "scheduler_running": scheduler_service.is_running
    }

# ============================================================================
# MANEJO DE ERRORES
# ============================================================================

@app.exception_handler(404)
async def not_found_handler(request, exc):
    return {"success": False, "message": "Recurso no encontrado"}

@app.exception_handler(422)
async def validation_error_handler(request, exc):
    return {"success": False, "message": "Error de validación", "details": exc.detail}

@app.exception_handler(500)
async def internal_error_handler(request, exc):
    return {"success": False, "message": "Error interno del servidor"}

# ============================================================================
# EJECUTAR SERVIDOR
# ============================================================================

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.debug
    )
    