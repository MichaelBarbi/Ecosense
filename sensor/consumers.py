import json
from channels.generic.websocket import AsyncWebsocketConsumer

class SensorConsumer(AsyncWebsocketConsumer):
    
    # Called when a WebSocket connection is opened
    async def connect(self):

        # Get the sensor ID from the URL route 
        self.sensor_id = self.scope['url_route']['kwargs']['sensor_id']

        # Define a group name to group all connections for this sensor
        self.sensor_group_name = f"sensor_{self.sensor_id}"

        # Add this WebSocket connection to the group
        await self.channel_layer.group_add(
            self.sensor_group_name,
            self.channel_name  # Internal channel name for this WebSocket connection
        )

        # Accept the WebSocket connection
        await self.accept()

    # Called when the WebSocket connection is closed
    async def disconnect(self, close_code):
        
        # Remove the connection from the group
        await self.channel_layer.group_discard(
            self.sensor_group_name,
            self.channel_name
        )

    # Custom method to send sensor data to the client
    async def send_sensor_data(self, event):
        # Send the sensor data (event["data"]) as JSON over WebSocket
        await self.send(text_data=json.dumps(event["data"]))

class GroupConsumer(AsyncWebsocketConsumer):

    # Called when a WebSocket connection is opened
    async def connect(self):

        # Get the group ID from the URL route
        self.group_id = self.scope['url_route']['kwargs']['group_id']

        # Define a group name to group all connections in this group
        self.group_name = f"group_{self.group_id}"

        # Add this WebSocket connection to the group
        await self.channel_layer.group_add(
            self.group_name,
            self.channel_name
        )

        # Accept the WebSocket connection
        await self.accept()

    # Called when the WebSocket connection is closed
    async def disconnect(self, close_code):
        # Remove the connection from the group
        await self.channel_layer.group_discard(
            self.group_name,
            self.channel_name
        )

    # Called when a message is received from the WebSocket client
    async def receive(self, text_data):
        pass  # Currently does nothing; you can implement logic to handle incoming messages here

    # Custom method to send sensor data to the client
    async def send_sensor_data(self, event):
        # Send the sensor data (event["data"]) as JSON over WebSocket
        await self.send(text_data=json.dumps(event["data"]))
