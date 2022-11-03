import json
from asgiref.sync import async_to_sync
from channels.generic.websocket import WebsocketConsumer
import registration.models
import chat.models


class ChatConsumer(WebsocketConsumer):
    def connect(self):
        self.room_name = self.scope['url_route']['kwargs']['room_name']
        self.room_group_name = 'chat_%s' % self.room_name


        # Join room group
        async_to_sync(self.channel_layer.group_add)(
            self.room_group_name,
            self.channel_name
        )

        self.accept()

    def disconnect(self, close_code):
        # Leave room group
        async_to_sync(self.channel_layer.group_discard)(
            self.room_group_name,
            self.channel_name
        )

    def save_message(self, message, sender, receiver):
        sender_user = registration.models.User.objects.get(id=sender)
        receiver_user = registration.models.User.objects.get(id=receiver)
        new_message = chat.models.Message.objects.create(message=message, sender_user=sender_user,
                                                         receiver_user=receiver_user)
        new_message.save()

    # def delete_message(self, message, sender, receiver):
    #     sender_user = registration.models.User.objects.get(id=sender)
    #     receiver_user = registration.models.User.objects.get(id=receiver)
    #     message = chat.models.Message.objects.filter(sender_user=sender_user,receiver_user=receiver_user).delete()
    #     new_message.save()

    # Receive message from WebSocket
    def receive(self, text_data):
        text_data_json = json.loads(text_data)
        print(text_data_json)
        message = text_data_json['message']
        sender = text_data_json['sender']
        receiver = text_data_json['receiver']
        sender_name = text_data_json['sender_name']
        self.save_message(message, sender, receiver)
        # self.send(text_data =json.dumps({'message': message}))

        # Send message to room group
        async_to_sync(self.channel_layer.group_send)(
            self.room_group_name,
            {
                'type': 'chat_message',
                'message': message,
                "sender": sender,
                "receiver": receiver,
                "sender_name": sender_name,
            }
        )

    # Receive message from room group
    def chat_message(self, event):
        message = event['message']
        sender = event['sender']
        receiver = event['receiver']
        sender_name = event['sender_name']


        # Send message to WebSocket
        self.send(text_data=json.dumps({
            'message': message,
            'sender': sender,
            'receiver': receiver,
            'sender_name': sender_name,
        }))
