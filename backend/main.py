from fastapi import FastAPI, Depends, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from sqlalchemy import and_, desc
from datetime import datetime, timezone
from typing import List, Optional
import uvicorn
import logging
import sys

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler('whatsapp_scheduler.log')
    ]
)
logger = logging.getLogger(__name__)

# Imports del proyecto
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

# Manejador global de excepciones
@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    logger.error(f"Error no manejado en {request.url}: {exc}")
    return JSONResponse(
        status_code=500,
        content={
            "success": False,
            "message": "Error interno del servidor",
            "error_type": type(exc).__name__
        }
    )

@app.on_event("startup")
async def startup_event():
    """Eventos al iniciar la aplicación"""
    try:
        logger.info("🚀 Iniciando WhatsApp Scheduler API...")
        
        # Crear tablas
        create_tables()
        logger.info("📊 Base de datos inicializada")
        
        # Iniciar scheduler de forma segura
        try:
            scheduler_service.start()
            logger.info("⚡ Scheduler iniciado exitosamente")
        except Exception as e:
            logger.error(f"❌ Error iniciando scheduler: {e}")
            # No terminar la aplicación, solo loggear el error
            
        logger.info("✅ Aplicación iniciada correctamente")
        
    except Exception as e:
        logger.error(f"❌ Error crítico en startup: {e}")

@app.on_event("shutdown")
async def shutdown_event():
    """Eventos al cerrar la aplicación"""
    try:
        logger.info("🛑 Cerrando WhatsApp Scheduler API...")
        
        if scheduler_service:
            scheduler_service.stop()
            logger.info("⚡ Scheduler detenido")
            
        logger.info("✅ Aplicación cerrada correctamente")
        
    except Exception as e:
        logger.error(f"❌ Error en shutdown: {e}")

# ============================================================================
# ENDPOINTS PRINCIPALES
# ============================================================================

@app.get("/", response_model=APIResponse)
async def root():
    """Endpoint de prueba"""
    try:
        return APIResponse(
            success=True,
            message=f"WhatsApp Scheduler API v{settings.app_version} está funcionando",
            data={
                "whatsapp_configured": bool(settings.whatsapp_access_token),
                "scheduler_running": scheduler_service.is_running,
                "timezone": settings.scheduler_timezone,
                "jobs_count": scheduler_service.get_job_count()
            }
        )
    except Exception as e:
        logger.error(f"Error en endpoint root: {e}")
        raise HTTPException(status_code=500, detail="Error obteniendo información del sistema")

@app.get("/health")
async def health_check():
    """Health check detallado"""
    try:
        health_status = {
            "api": "healthy",
            "database": "unknown",
            "scheduler": "unknown",
            "whatsapp": "unknown",
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
        
        # Verificar BD
        try:
            db = next(get_db())
            db.execute("SELECT 1")
            health_status["database"] = "healthy"
            db.close()
        except Exception as e:
            health_status["database"] = f"error: {str(e)}"
        
        # Verificar scheduler
        try:
            if scheduler_service.is_running:
                health_status["scheduler"] = f"running ({scheduler_service.get_job_count()} jobs)"
            else:
                health_status["scheduler"] = "stopped"
        except Exception as e:
            health_status["scheduler"] = f"error: {str(e)}"
        
        # Verificar WhatsApp
        health_status["whatsapp"] = "configured" if settings.whatsapp_access_token else "not_configured"
        
        return health_status
        
    except Exception as e:
        logger.error(f"Error en health check: {e}")
        raise HTTPException(status_code=500, detail="Error en health check")

@app.post("/api/schedule", response_model=ScheduledMessageResponse)
async def create_scheduled_message(
    message: ScheduledMessageCreate,
    db: Session = Depends(get_db)
):
    """Crear un nuevo mensaje programado"""
    try:
        logger.info(f"Creando mensaje para {message.phone} a las {message.send_time}")
        
        # Validar que la fecha sea futura
        now = datetime.now(timezone.utc)
        send_time_utc = message.send_time.replace(tzinfo=timezone.utc)
        
        if send_time_utc <= now:
            raise HTTPException(
                status_code=400,
                detail="La fecha de envío debe ser en el futuro"
            )
        
        # Crear mensaje en la base de datos
        db_message = ScheduledMessage(
            phone=message.phone,
            message=message.message,
            send_time=send_time_utc,
            created_at=now,
            updated_at=now
        )
        
        db.add(db_message)
        db.commit()
        db.refresh(db_message)
        
        logger.info(f"Mensaje creado en BD con ID: {db_message.id}")
        
        # Programar el envío
        if scheduler_service.is_running:
            schedule_success = await scheduler_service.schedule_message(
                db_message.id, 
                send_time_utc
            )
            
            if not schedule_success:
                logger.error(f"Error programando mensaje {db_message.id}")
                # No eliminar el mensaje, solo loggear
        else:
            logger.warning("Scheduler no está corriendo, mensaje creado pero no programado")
        
        return db_message
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creando mensaje programado: {e}")
        raise HTTPException(status_code=500, detail="Error interno creando mensaje")

@app.get("/api/scheduled", response_model=MessageListResponse)
async def get_scheduled_messages(
    page: int = Query(1, ge=1, description="Página"),
    per_page: int = Query(50, ge=1, le=100, description="Mensajes por página"),
    status: Optional[str] = Query(None, description="Filtrar por estado: pending, sent, failed"),
    phone: Optional[str] = Query(None, description="Filtrar por número de teléfono"),
    db: Session = Depends(get_db)
):
    """Obtener lista de mensajes programados con filtros y paginación"""
    try:
        # Base query
        query = db.query(ScheduledMessage)
        
        # Aplicar filtros
        if status:
            now = datetime.now(timezone.utc)
            if status == "pending":
                query = query.filter(and_(
                    ScheduledMessage.is_sent == False,
                    ScheduledMessage.send_time > now,
                    ScheduledMessage.error_message == None
                ))
            elif status == "sent":
                query = query.filter(ScheduledMessage.is_sent == True)
            elif status == "failed":
                query = query.filter(and_(
                    ScheduledMessage.is_sent == False,
                    ScheduledMessage.error_message != None
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
        
    except Exception as e:
        logger.error(f"Error obteniendo mensajes: {e}")
        raise HTTPException(status_code=500, detail="Error obteniendo lista de mensajes")

@app.get("/api/scheduled/{message_id}", response_model=ScheduledMessageResponse)
async def get_scheduled_message(message_id: int, db: Session = Depends(get_db)):
    """Obtener un mensaje programado específico"""
    try:
        message = db.query(ScheduledMessage).filter(ScheduledMessage.id == message_id).first()
        
        if not message:
            raise HTTPException(status_code=404, detail="Mensaje no encontrado")
        
        return message
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error obteniendo mensaje {message_id}: {e}")
        raise HTTPException(status_code=500, detail="Error obteniendo mensaje")

@app.put("/api/scheduled/{message_id}", response_model=ScheduledMessageResponse)
async def update_scheduled_message(
    message_id: int,
    message_update: ScheduledMessageUpdate,
    db: Session = Depends(get_db)
):
    """Actualizar un mensaje programado"""
    try:
        logger.info(f"Actualizando mensaje {message_id}")
        
        message = db.query(ScheduledMessage).filter(ScheduledMessage.id == message_id).first()
        
        if not message:
            raise HTTPException(status_code=404, detail="Mensaje no encontrado")
        
        if message.is_sent:
            raise HTTPException(status_code=400, detail="No se puede editar un mensaje ya enviado")
        
        # Actualizar campos
        update_data = message_update.dict(exclude_unset=True)
        
        for field, value in update_data.items():
            setattr(message, field, value)
        
        message.updated_at = datetime.now(timezone.utc)
        
        db.commit()
        db.refresh(message)
        
        # Re-programar si cambió la fecha
        if message_update.send_time and scheduler_service.is_running:
            await scheduler_service.schedule_message(message.id, message_update.send_time)
        
        return message
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error actualizando mensaje {message_id}: {e}")
        raise HTTPException(status_code=500, detail="Error actualizando mensaje")

@app.delete("/api/scheduled/{message_id}", response_model=APIResponse)
async def delete_scheduled_message(message_id: int, db: Session = Depends(get_db)):
    """Eliminar un mensaje programado"""
    try:
        logger.info(f"Eliminando mensaje {message_id}")
        
        message = db.query(ScheduledMessage).filter(ScheduledMessage.id == message_id).first()
        
        if not message:
            raise HTTPException(status_code=404, detail="Mensaje no encontrado")
        
        # Cancelar el job programado
        if scheduler_service.is_running:
            await scheduler_service.cancel_message(message_id)
        
        # Eliminar de la base de datos
        db.delete(message)
        db.commit()
        
        return APIResponse(
            success=True,
            message=f"Mensaje {message_id} eliminado correctamente"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error eliminando mensaje {message_id}: {e}")
        raise HTTPException(status_code=500, detail="Error eliminando mensaje")

# ============================================================================
# ENDPOINTS DE TESTING Y UTILIDADES
# ============================================================================

@app.post("/api/send-now", response_model=MessageSendResponse)
async def send_message_now(message: MessageSendRequest):
    """Enviar un mensaje inmediatamente (para testing)"""
    try:
        logger.info(f"Enviando mensaje inmediato a {message.phone}")
        
        result = await whatsapp_service.send_message(
            phone=message.phone,
            message=message.message
        )
        
        return MessageSendResponse(
            success=result.get('success', False),
            message_id=result.get('message_id'),
            status=result.get('status', 'unknown'),
            timestamp=datetime.now(timezone.utc),
            error=result.get('error')
        )
        
    except Exception as e:
        logger.error(f"Error enviando mensaje inmediato: {e}")
        return MessageSendResponse(
            success=False,
            message_id=None,
            status='failed',
            timestamp=datetime.now(timezone.utc),
            error=str(e)
        )

@app.get("/api/stats")
async def get_stats(db: Session = Depends(get_db)):
    """Obtener estadísticas del sistema"""
    try:
        now = datetime.now(timezone.utc)
        
        total_messages = db.query(ScheduledMessage).count()
        sent_messages = db.query(ScheduledMessage).filter(ScheduledMessage.is_sent == True).count()
        pending_messages = db.query(ScheduledMessage).filter(
            and_(
                ScheduledMessage.is_sent == False,
                ScheduledMessage.send_time > now,
                ScheduledMessage.error_message == None
            )
        ).count()
        failed_messages = db.query(ScheduledMessage).filter(
            and_(
                ScheduledMessage.is_sent == False,
                ScheduledMessage.error_message != None
            )
        ).count()
        
        return {
            "total_messages": total_messages,
            "sent_messages": sent_messages,
            "pending_messages": pending_messages,
            "failed_messages": failed_messages,
            "success_rate": round((sent_messages / total_messages * 100), 2) if total_messages > 0 else 0,
            "scheduler_running": scheduler_service.is_running,
            "scheduler_jobs": scheduler_service.get_job_count(),
            "next_jobs": scheduler_service.get_next_jobs(3)
        }
        
    except Exception as e:
        logger.error(f"Error obteniendo estadísticas: {e}")
        raise HTTPException(status_code=500, detail="Error obteniendo estadísticas")

@app.get("/api/scheduler/status")
async def get_scheduler_status():
    """Obtener estado detallado del scheduler"""
    try:
        return {
            "running": scheduler_service.is_running,
            "job_count": scheduler_service.get_job_count(),
            "next_jobs": scheduler_service.get_next_jobs(5),
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
    except Exception as e:
        logger.error(f"Error obteniendo estado del scheduler: {e}")
        raise HTTPException(status_code=500, detail="Error obteniendo estado del scheduler")

# ============================================================================
# EJECUTAR SERVIDOR
# ============================================================================

if __name__ == "__main__":
    logger.info("🚀 Iniciando servidor WhatsApp Scheduler...")
    
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=False,  # Deshabilitado para evitar problemas con scheduler
        log_level="info"
    )