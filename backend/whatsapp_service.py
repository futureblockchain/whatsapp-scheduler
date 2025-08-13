import httpx
from settings import settings
from datetime import datetime
from typing import Dict, Any

class WhatsAppService:
    """
    Servicio para enviar mensajes de WhatsApp usando la API Cloud oficial de Meta.
    """

    def __init__(self):
        self.base_url = f"{settings.whatsapp_api_base}/{settings.whatsapp_api_version}"
        self.phone_number_id = settings.whatsapp_phone_number_id
        self.headers = {
            "Authorization": f"Bearer {settings.whatsapp_access_token}",
            "Content-Type": "application/json"
        }
        # Modo simulación si no hay token o phone number id configurados
        self.simulate_mode = not (settings.whatsapp_access_token and settings.whatsapp_phone_number_id)
        if self.simulate_mode:
            print("🔄 WhatsApp Service iniciado en MODO SIMULACIÓN")
        else:
            print("📱 WhatsApp Service iniciado con API REAL de Meta")

    async def send_message(self, phone: str, message: str) -> Dict[str, Any]:
        """
        Envía un mensaje de texto a un número usando la API oficial de WhatsApp Cloud.
        
        Args:
            phone: Número en formato E.164, por ejemplo "+521234567890" o "+15551234567"
            message: Texto del mensaje a enviar
        
        Returns:
            Diccionario con el resultado del envío.
        """
        if self.simulate_mode:
            return await self._simulate_send(phone, message)
        else:
            return await self._real_send(phone, message)

    async def _simulate_send(self, phone: str, message: str) -> Dict[str, Any]:
        """
        Simula el envío de un mensaje para desarrollo/testing.
        """
        import asyncio
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
        Envía el mensaje real mediante la API oficial.
        """
        url = f"{self.base_url}/{self.phone_number_id}/messages"
        payload = {
            "messaging_product": "whatsapp",
            "to": phone,
            "type": "text",
            "text": {
                "body": message,
                "preview_url": False
            }
        }
        try:
            async with httpx.AsyncClient(timeout=15) as client:
                response = await client.post(url, headers=self.headers, json=payload)
                try:
                    data = response.json()
                except Exception:
                    data = {"error": {"message": response.text}}

                if response.status_code in (200, 201):
                    print(f"✅ Mensaje enviado exitosamente a {phone}")
                    return {
                        "success": True,
                        "message_id": data.get("messages", [{}])[0].get("id"),
                        "status": "sent",
                        "timestamp": datetime.now().isoformat()
                    }
                else:
                    print(f"❌ Error enviando mensaje: {data}")
                    return {
                        "success": False,
                        "error": data.get("error", {}).get("message", "Error desconocido"),
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

# Instancia global
whatsapp_service = WhatsAppService()