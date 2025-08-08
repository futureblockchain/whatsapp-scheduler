import asyncio
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.date import DateTrigger
from apscheduler.triggers.interval import IntervalTrigger
from datetime import datetime
from sqlalchemy.orm import Session
from sqlalchemy import and_

from database import SessionLocal, get_db
from models import ScheduledMessage
from whatsapp_service import whatsapp_service
from settings import settings

class MessageSchedulerService:
    """
    Servicio para programar y enviar mensajes automáticamente.
    Usa APScheduler para manejar los jobs de envío.
    """
    
    def __init__(self):
        self.scheduler = AsyncIOScheduler(timezone=settings.scheduler_timezone)
        self.is_running = False
        
    def start(self):
        """Iniciar el scheduler"""
        if not self.is_running:
            # Programar verificación periódica de mensajes pendientes
            self.scheduler.add_job(
                func=self._check_pending_messages,
                trigger=IntervalTrigger(seconds=settings.check_interval_seconds),
                id='check_pending_messages',
                name='Verificar mensajes pendientes',
                replace_existing=True
            )
            
            self.scheduler.start()
            self.is_running = True
            print(f"📅 Scheduler iniciado - verificando cada {settings.check_interval_seconds}s")
            
            # Cargar mensajes pendientes al iniciar
            asyncio.create_task(self._reschedule_pending_messages())
    
    def stop(self):
        """Detener el scheduler"""
        if self.is_running:
            self.scheduler.shutdown()
            self.is_running = False
            print("📅 Scheduler detenido")
    
    async def schedule_message(self, message_id: int, send_time: datetime):
        """
        Programar un mensaje específico para envío.
        
        Args:
            message_id: ID del mensaje en la base de datos
            send_time: Fecha y hora de envío
        """
        job_id = f"send_message_{message_id}"
        
        # Remover job existente si existe
        if self.scheduler.get_job(job_id):
            self.scheduler.remove_job(job_id)
        
        # Programar nuevo job
        self.scheduler.add_job(
            func=self._send_scheduled_message,
            trigger=DateTrigger(run_date=send_time),
            args=[message_id],
            id=job_id,
            name=f"Enviar mensaje {message_id}",
            replace_existing=True
        )
        
        print(f"📅 Mensaje {message_id} programado para {send_time}")
    
    async def cancel_message(self, message_id: int):
        """Cancelar el envío programado de un mensaje"""
        job_id = f"send_message_{message_id}"
        
        if self.scheduler.get_job(job_id):
            self.scheduler.remove_job(job_id)
            print(f"📅 Envío cancelado para mensaje {message_id}")
        
    async def _check_pending_messages(self):
        """
        Verificar mensajes pendientes que deberían enviarse ya.
        Este es un mecanismo de respaldo en caso de que fallen los jobs programados.
        """
        try:
            db = SessionLocal()
            now = datetime.now()
            
            # Buscar mensajes que deberían haberse enviado pero no se han enviado
            overdue_messages = db.query(ScheduledMessage).filter(
                and_(
                    ScheduledMessage.is_sent == False,
                    ScheduledMessage.send_time <= now
                )
            ).all()
            
            for message in overdue_messages:
                print(f"⚠️ Enviando mensaje atrasado {message.id}")
                await self._send_scheduled_message(message.id)
                
            db.close()
            
        except Exception as e:
            print(f"❌ Error verificando mensajes pendientes: {str(e)}")
    
    async def _reschedule_pending_messages(self):
        """
        Re-programar todos los mensajes pendientes al iniciar el servidor.
        Útil después de reiniciar la aplicación.
        """
        try:
            db = SessionLocal()
            now = datetime.now()
            
            # Buscar mensajes pendientes futuros
            pending_messages = db.query(ScheduledMessage).filter(
                and_(
                    ScheduledMessage.is_sent == False,
                    ScheduledMessage.send_time > now
                )
            ).all()
            
            for message in pending_messages:
                await self.schedule_message(message.id, message.send_time)
            
            print(f"📅 Re-programados {len(pending_messages)} mensajes pendientes")
            db.close()
            
        except Exception as e:
            print(f"❌ Error re-programando mensajes: {str(e)}")
    
    async def _send_scheduled_message(self, message_id: int):
        """
        Enviar un mensaje programado específico.
        
        Args:
            message_id: ID del mensaje en la base de datos
        """
        db = SessionLocal()
        
        try:
            # Buscar el mensaje
            message = db.query(ScheduledMessage).filter(
                ScheduledMessage.id == message_id
            ).first()
            
            if not message:
                print(f"❌ Mensaje {message_id} no encontrado")
                return
            
            if message.is_sent:
                print(f"⚠️ Mensaje {message_id} ya fue enviado")
                return
            
            # Intentar enviar el mensaje
            print(f"📤 Enviando mensaje {message_id} a {message.phone}")
            
            result = await whatsapp_service.send_message(
                phone=message.phone,
                message=message.message
            )
            
            # Actualizar estado en la base de datos
            message.sent_at = datetime.now()
            
            if result.get('success'):
                message.is_sent = True
                message.error_message = None
                print(f"✅ Mensaje {message_id} enviado exitosamente")
            else:
                message.error_message = result.get('error', 'Error desconocido')
                print(f"❌ Error enviando mensaje {message_id}: {message.error_message}")
            
            db.commit()
            
        except Exception as e:
            print(f"❌ Excepción enviando mensaje {message_id}: {str(e)}")
            
            # Actualizar con error en la BD
            message = db.query(ScheduledMessage).filter(
                ScheduledMessage.id == message_id
            ).first()
            
            if message:
                message.error_message = str(e)
                message.sent_at = datetime.now()
                db.commit()
        
        finally:
            db.close()

# Instancia global del scheduler
scheduler_service = MessageSchedulerService()