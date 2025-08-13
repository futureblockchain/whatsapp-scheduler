import asyncio
import logging
from datetime import datetime, timezone
from typing import Optional
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.jobstores.sqlalchemy import SQLAlchemyJobStore
from apscheduler.executors.pool import ThreadPoolExecutor
from sqlalchemy.orm import Session
from database import SessionLocal, engine
from models import ScheduledMessage
from message_sender import send_scheduled_message

# Configurar logging
logger = logging.getLogger(__name__)

class MessageSchedulerService:
    def __init__(self):
        # Configuración más conservadora del scheduler
        jobstores = {
            'default': SQLAlchemyJobStore(engine=engine, tablename='apscheduler_jobs')
        }
        executors = {
            'default': ThreadPoolExecutor(max_workers=3)  # Reducir workers
        }
        job_defaults = {
            'coalesce': True,
            'max_instances': 1,
            'misfire_grace_time': 60  # 1 minuto de gracia
        }
        
        self.scheduler = AsyncIOScheduler(
            jobstores=jobstores,
            executors=executors,
            job_defaults=job_defaults,
            timezone=timezone.utc
        )
        
        self._running = False
        self._shutdown_requested = False

    @property
    def is_running(self) -> bool:
        """Verificar si el scheduler está corriendo"""
        return self._running and self.scheduler.running


    async def schedule_message(self, message_id: int, send_time: datetime) -> bool:
        """Programar un mensaje para envío"""
        try:
            if self._shutdown_requested:
                logger.warning("No se pueden programar mensajes durante shutdown")
                return False
            
            # Validar que la fecha sea futura
            now = datetime.now(timezone.utc)
            if send_time.replace(tzinfo=timezone.utc) <= now:
                logger.error(f"Fecha de envío {send_time} debe ser futura")
                return False
            
            job_id = f"whatsapp_message_{message_id}"
            
            # Remover job existente si existe
            try:
                self.scheduler.remove_job(job_id)
                logger.info(f"Job existente {job_id} removido")
            except:
                pass  # Job no existía
            
            # Programar nuevo job usando la función independiente
            self.scheduler.add_job(
                func=send_scheduled_message,
                args=[message_id],
                trigger='date',
                run_date=send_time.replace(tzinfo=timezone.utc),
                id=job_id,
                replace_existing=True
            )
            
            logger.info(f"Mensaje ID {message_id} programado para {send_time} UTC")
            return True
            
        except Exception as e:
            logger.error(f"Error programando mensaje {message_id}: {e}")
            return False

    async def cancel_message(self, message_id: int) -> bool:
        """Cancelar un mensaje programado"""
        try:
            job_id = f"whatsapp_message_{message_id}"
            
            try:
                self.scheduler.remove_job(job_id)
                logger.info(f"Job {job_id} cancelado")
                return True
            except:
                logger.warning(f"Job {job_id} no encontrado para cancelar")
                return True  # Considerar como exitoso si no existe
                
        except Exception as e:
            logger.error(f"Error cancelando mensaje {message_id}: {e}")
            return False

    def start(self):
        """Iniciar el scheduler"""
        try:
            if not self.scheduler.running:
                self.scheduler.start()
                self._running = True
                logger.info("Scheduler iniciado exitosamente")
                
                # Cargar mensajes pendientes
                self._load_pending_messages()
            else:
                logger.warning("Scheduler ya está corriendo")
                
        except Exception as e:
            logger.error(f"Error iniciando scheduler: {e}")
            raise

    def stop(self):
        """Detener el scheduler"""
        try:
            self._shutdown_requested = True
            
            if self.scheduler.running:
                self.scheduler.shutdown(wait=True)
                logger.info("Scheduler detenido")
            
            self._running = False
            
        except Exception as e:
            logger.error(f"Error deteniendo scheduler: {e}")

    def _load_pending_messages(self):
        """Cargar mensajes pendientes desde la BD al iniciar"""
        try:
            db = SessionLocal()
            try:
                # Buscar mensajes no enviados con fecha futura
                now = datetime.now(timezone.utc)
                pending_messages = db.query(ScheduledMessage).filter(
                    ScheduledMessage.is_sent == False,
                    ScheduledMessage.send_time > now,
                    ScheduledMessage.error_message == None  # Solo los que no han fallado
                ).all()
                
                loaded_count = 0
                for message in pending_messages:
                    # Usar asyncio.create_task de forma segura
                    try:
                        # Programar directamente usando función independiente
                        job_id = f"whatsapp_message_{message.id}"
                        self.scheduler.add_job(
                            func=send_scheduled_message,
                            args=[message.id],
                            trigger='date',
                            run_date=message.send_time.replace(tzinfo=timezone.utc),
                            id=job_id,
                            replace_existing=True
                        )
                        loaded_count += 1
                    except Exception as e:
                        logger.error(f"Error cargando mensaje {message.id}: {e}")
                
                logger.info(f"Cargados {loaded_count} mensajes pendientes")
                
            finally:
                db.close()
                
        except Exception as e:
            logger.error(f"Error cargando mensajes pendientes: {e}")

    def get_job_count(self) -> int:
        """Obtener número de jobs programados"""
        try:
            return len(self.scheduler.get_jobs())
        except:
            return 0

    def get_next_jobs(self, limit: int = 5) -> list:
        """Obtener próximos jobs programados"""
        try:
            jobs = self.scheduler.get_jobs()
            # Ordenar por próxima ejecución
            jobs.sort(key=lambda x: x.next_run_time or datetime.max.replace(tzinfo=timezone.utc))
            
            return [
                {
                    'id': job.id,
                    'next_run_time': job.next_run_time.isoformat() if job.next_run_time else None,
                    'trigger': str(job.trigger)
                }
                for job in jobs[:limit]
            ]
        except Exception as e:
            logger.error(f"Error obteniendo jobs: {e}")
            return []

# Instancia global del scheduler
scheduler_service = MessageSchedulerService()