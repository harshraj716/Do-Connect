from chat.models import Chat, Room
import json
from channels.generic.websocket import AsyncWebsocketConsumer
from django.contrib.auth.models import User
from django.core.exceptions import ObjectDoesNotExist
import logging

logger = logging.getLogger(__name__)

class ChatRoomConsumer(AsyncWebsocketConsumer):

    async def connect(self):
        self.room_name = self.scope['url_route']['kwargs']['room_name']
        self.room_group_name = f'chat_{self.room_name}'

        logger.info(f"Connecting to room {self.room_name}")

        try:
            await self.channel_layer.group_add(
                self.room_group_name,
                self.channel_name
            )

            await self.accept()
            logger.info(f"WebSocket connection established for room {self.room_name}")

        except Exception as e:
            logger.error(f"Failed to establish WebSocket connection: {e}")

    async def disconnect(self, close_code):
        logger.info(f"Disconnecting from room {self.room_name}")

        try:
            await self.channel_layer.group_discard(
                self.room_group_name,
                self.channel_name
            )
            logger.info(f"WebSocket connection closed for room {self.room_name}")

        except Exception as e:
            logger.error(f"Failed to close WebSocket connection: {e}")

    async def receive(self, text_data):
        try:
            text_data_json = json.loads(text_data)
            message = text_data_json['message']
            username = text_data_json['username']
            user_image = text_data_json['user_image']

            await self.save_message(username, message)

            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'chatroom_message',
                    'message': message,
                    'username': username,
                    'user_image': user_image,
                }
            )

        except json.JSONDecodeError:
            # Handle JSON decoding error
            await self.send_error_message("Invalid JSON data")
            logger.error("Invalid JSON data received")

        except KeyError as e:
            # Handle missing key in JSON data
            await self.send_error_message(f"Missing key: {e}")
            logger.error(f"Missing key in JSON data: {e}")

        except Exception as e:
            logger.error(f"Failed to process received data: {e}")

    async def chatroom_message(self, event):
        message = event['message']
        username = event['username']
        user_image = event['user_image']

        await self.send(text_data=json.dumps({
            'message': message,
            'username': username,
            'user_image': user_image,
        }))

    async def save_message(self, username, message):
        try:
            author_user = await self.get_user(username)
            room = await self.get_room()

            await self.create_new_message(author_user, message, room)
        except ObjectDoesNotExist:
            # Handle user or room not found
            await self.send_error_message("User or room not found")
            logger.error("User or room not found")

    async def create_new_message(self, author_user, message, room):
        Chat.objects.create(
            author=author_user,
            room_id=room,
            text=message
        )

    async def get_user(self, username):
        return User.objects.get(username=username)

    async def get_room(self):
        try:
            return Room.objects.get(room_id=self.room_name)
        except Room.DoesNotExist:
            # Handle room not found
            await self.send_error_message("Room not found")
            logger.error("Room not found")

    async def send_error_message(self, error_message):
        await self.send(text_data=json.dumps({
            'error': error_message,
        }))
