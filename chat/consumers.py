import asyncio
import json
from threading import Timer

from asgiref.sync import sync_to_async
from channels.generic.websocket import AsyncJsonWebsocketConsumer

from chat.managers import ChatManager


class ChatConsumer(AsyncJsonWebsocketConsumer):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.room_name = ''
        self.room_group_name = ''
        self._timeout = None
        self._manager = ChatManager(self)

    async def set_group(self):
        self.room_name = self._manager.room_name
        await self.channel_layer.group_add(
            self.room_name,
            self.channel_name
        )

    async def connect(self):
        await self.accept()
        await self.send_response("info", "Waiting user token...")

        self._timeout = Timer(5.0, lambda: asyncio.run(self._timeout_connection()))
        self._timeout.start()

    async def _timeout_connection(self):
        await self.send_response("authorization_response", {
            "accepted": False,
            "message": "Authorization failed, connection timeout."
        })
        await self.close()

    async def timeout_stop(self):
        if self._timeout is not None:
            self._timeout.cancel()
            self._timeout = None

    async def send_response(self, response_type: str, data):
        await self.send_json({
            "type": response_type,
            "data": data
        })

    async def send_message(self, data):
        await self.send_response(data["data"]["type"], data["data"]["data"])

    async def disconnect(self, code):
        await sync_to_async(print)(self._manager.room_name)
        await self._manager.on_disconnect()
        if self._manager.room_name:
            await self.channel_layer.group_discard(
                self._manager.room_name,
                self.channel_name
            )

    async def receive_json(self, content, **kwargs):
        await self._manager.route_resolve(content)

