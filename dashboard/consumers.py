"""
WebSocket consumers for real-time updates
"""

import json
import logging
from channels.generic.websocket import AsyncWebsocketConsumer
from asgiref.sync import sync_to_async
from datetime import datetime

logger = logging.getLogger(__name__)


class DashboardConsumer(AsyncWebsocketConsumer):
    """Consumer para atualizações em tempo real do dashboard"""
    
    async def connect(self):
        """Quando cliente se conecta"""
        await self.channel_layer.group_add("dashboard", self.channel_name)
        await self.accept()
        
        logger.info(f"Cliente conectado: {self.channel_name}")
        
        # Enviar dados atuais
        from .views import current_data
        await self.send(text_data=json.dumps({
            'type': 'update',
            'data': current_data
        }))
    
    async def disconnect(self, close_code):
        """Quando cliente se desconecta"""
        await self.channel_layer.group_discard("dashboard", self.channel_name)
        logger.info(f"Cliente desconectado: {self.channel_name}")
    
    async def receive(self, text_data):
        """Receber mensagem do cliente"""
        pass
    
    async def dashboard_update(self, event):
        """Enviar atualização para o cliente"""
        await self.send(text_data=json.dumps({
            'type': 'update',
            'data': event['data']
        }))
