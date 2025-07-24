import json
from channels.generic.websocket import AsyncWebsocketConsumer

class SensorConsumer(AsyncWebsocketConsumer):
    
    async def connect(self):
        self.sensor_id = self.scope['url_route']['kwargs']['sensor_id']
        self.sensor_group_name = f"sensor_{self.sensor_id}"

        await self.channel_layer.group_add(
            self.sensor_group_name,
            self.channel_name
        )

        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(
            self.sensor_group_name,
            self.channel_name
        )

    async def send_sensor_data(self, event):
        await self.send(text_data=json.dumps(event["data"]))


class GroupConsumer(AsyncWebsocketConsumer):

    async def connect(self):
        self.group_id = self.scope['url_route']['kwargs']['group_id']
        self.group_name = f"group_{self.group_id}"

        await self.channel_layer.group_add(
            self.group_name,
            self.channel_name
        )

        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(
            self.group_name,
            self.channel_name
        )

    async def receive(self, text_data):
        pass

    async def send_sensor_data(self, event):
        await self.send(text_data=json.dumps(event["data"]))
