import os
import httpx
from datetime import datetime
from typing import Dict, Any
import asyncio

class WhatsAppService:
    """
    Servicio para enviar mensajes de WhatsApp.
    Incluye implementación real para API de Meta y versión simulada.
    """
    
    def __init__(self):
        self.whatsapp_token = os.getenv("WHATSAPP_ACCESS_TOKEN")
        self.whatsapp_phone_id = os.getenv("WHATSAPP_PHONE_NUMBER_ID")
        self.base_url = "https://graph.facebook.com/v18.0"
        self.simulate_mode = not (self.whatsapp_token and self.whatsapp_phone_id)
        
        if self.simulate_mode:
            print("🔄 WhatsApp Service iniciado en MODO SIMULACIÓN")
        else:
            print("📱 WhatsApp Service iniciado con API REAL de Meta")
    
    async def send_message(self, phone: str, message: str) -> Dict[str, Any]:
        """
        Envía un mensaje de WhatsApp.
        
        Args:
            phone: Número de teléfono (formato: +52XXXXXXXXXX)
            message: Mensaje a enviar
            
        Returns:
            Dict con resultado del envío
        """
        
        if self.simulate_mode:
            return await self._simulate_send(phone, message)
        else:
            return await self._real_send(phone, message)
    
    async def _simulate_send(self, phone: str, message: str) -> Dict[str, Any]:
        """
        Simula el envío de un mensaje para desarrollo/testing.
        """
        # Simular delay de red
        await asyncio.sleep(0.5)
        
        print(f"📨 MENSAJE SIMULADO ENVIADO:")
        print(f"   📞 Para: {phone}")
        print(f"   💬 Mensaje: {message[:50]}{'...' if len(message) > 50 else ''}")
        print(f"   🕐 Hora: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("-" * 50)
        
        return {
            "success": True,
            "message_id": f"sim_{datetime.now().timestamp()}",
            "status": "sent",
            "timestamp": datetime.now().isoformat()
        }
    
    async def _real_send(self, phone: str, message: str) -> Dict[str, Any]:
        """
        Envía un mensaje real usando la API de WhatsApp Business de Meta.
        """
        url = f"{self.base_url}/{self.whatsapp_phone_id}/messages"
        
        headers = {
            "Authorization": f"Bearer {self.whatsapp_token}",
            "Content-Type": "application/json"
        }
        
        # Limpiar número de teléfono (quitar espacios, guiones, etc.)
        clean_phone = ''.join(filter(str.isdigit, phone))
        if not clean_phone.startswith('52'):  # Agregar código de país México
            clean_phone = '52' + clean_phone
        
        payload = {
            "messaging_product": "whatsapp",
            "to": clean_phone,
            "type": "text",
            "text": {
                "body": message
            }
        }
        
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(url, json=payload, headers=headers)
                
                if response.status_code == 200:
                    data = response.json()
                    print(f"✅ Mensaje enviado exitosamente a {phone}")
                    return {
                        "success": True,
                        "message_id": data.get("messages", [{}])[0].get("id"),
                        "status": "sent",
                        "timestamp": datetime.now().isoformat()
                    }
                else:
                    error_data = response.json()
                    print(f"❌ Error enviando mensaje: {error_data}")
                    return {
                        "success": False,
                        "error": error_data.get("error", {}).get("message", "Error desconocido"),
                        "status": "failed",
                        "timestamp": datetime.now().isoformat()
                    }
                    
        except Exception as e:
            print(f"❌ Excepción enviando mensaje: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "status": "failed", 
                "timestamp": datetime.now().isoformat()
            }

# Instancia global del servicio
whatsapp_service = WhatsAppService()