import json
from asgiref.sync import async_to_sync
from channels.generic.websocket import WebsocketConsumer
import registration.models
import chat.models
from notifications.signals import notify


class ChatConsumer(WebsocketConsumer):
    def connect(self):
        self.room_name = self.scope['url_route']['kwargs']['room_name']
        self.room_group_name = 'chat_%s' % self.room_name


        async_to_sync(self.channel_layer.group_add)(
            self.room_group_name,
            self.channel_name
        )

        self.accept()

    def disconnect(self, close_code):
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
        notify.send(sender=sender_user, recipient=receiver_user,
                    verb='You have new message from {}'.format(sender_user.username))

    def receive(self, text_data):
        text_data_json = json.loads(text_data)
        print(text_data_json)
        message = text_data_json['message']
        sender = text_data_json['sender']
        receiver = text_data_json['receiver']
        sender_name = text_data_json['sender_name']
        self.save_message(message, sender, receiver)

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

    def chat_message(self, event):
        message = event['message']
        sender = event['sender']
        receiver = event['receiver']
        sender_name = event['sender_name']

        self.send(text_data=json.dumps({
            'message': message,
            'sender': sender,
            'receiver': receiver,
            'sender_name': sender_name,
        }))
