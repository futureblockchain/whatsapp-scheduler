"""
Módulo independiente para envío de mensajes programados.
No tiene dependencias del scheduler para evitar problemas de serialización.
"""
import asyncio
import logging
from datetime import datetime, timezone
from sqlalchemy.orm import Session
from database import SessionLocal
from models import ScheduledMessage

logger = logging.getLogger(__name__)

def send_scheduled_message(message_id: int):
    """
    Función independiente para enviar mensajes programados.
    No tiene referencias al scheduler para evitar problemas de serialización.
    """
    try:
        logger.info(f"Iniciando envío de mensaje ID: {message_id}")
        
        # Usar sesión síncrona de SQLAlchemy
        db = SessionLocal()
        try:
            # Buscar el mensaje
            message = db.query(ScheduledMessage).filter(
                ScheduledMessage.id == message_id
            ).first()
            
            if not message:
                logger.error(f"Mensaje ID {message_id} no encontrado")
                return
            
            if message.is_sent:
                logger.warning(f"Mensaje ID {message_id} ya fue enviado")
                return
            
            # Importar whatsapp_service localmente
            from whatsapp_service import whatsapp_service
            
            # Crear nuevo event loop para la operación asíncrona
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            
            try:
                # Enviar mensaje usando el servicio WhatsApp
                result = loop.run_until_complete(
                    whatsapp_service.send_message(message.phone, message.message)
                )
                
                # Actualizar estado del mensaje
                if result.get('success', False):
                    message.is_sent = True
                    message.sent_at = datetime.now(timezone.utc)
                    logger.info(f"Mensaje ID {message_id} enviado exitosamente")
                else:
                    message.error_message = result.get('error', 'Error desconocido')
                    logger.error(f"Error enviando mensaje ID {message_id}: {message.error_message}")
                
                # Actualizar timestamp
                message.updated_at = datetime.now(timezone.utc)
                db.commit()
                
            finally:
                loop.close()
                
        except Exception as e:
            logger.error(f"Error procesando mensaje ID {message_id}: {e}")
            try:
                # Intentar marcar el error en la BD
                message = db.query(ScheduledMessage).filter(
                    ScheduledMessage.id == message_id
                ).first()
                if message:
                    message.error_message = str(e)
                    message.updated_at = datetime.now(timezone.utc)
                    db.commit()
            except Exception as db_error:
                logger.error(f"Error actualizando BD para mensaje {message_id}: {db_error}")
        finally:
            db.close()
            
    except Exception as e:
        logger.error(f"Error crítico enviando mensaje {message_id}: {e}")