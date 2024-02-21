import json
from channels.consumer import AsyncConsumer

class ChatConsumer(AsyncConsumer):
    async def websocket_connect(self, event):
        self.room_name = "room"
        self.room_group_name = f"chatkse_{self.room_name}"
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )
        await self.send({
            "type": "websocket.accept"
        })

    async def websocket_disconnect(self, event):
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    async def websocket_receive(self, event):
        msg = json.loads(event["text"])
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                "type": "chat.message",
                "msg": msg
            }
        )

    async def chat_message(self, event):
        msg = event["msg"]
        await self.send({
            "type": "websocket.send",
            "text": json.dumps(msg)
        })

