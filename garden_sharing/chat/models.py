from django.contrib.auth.models import AnonymousUser
from django.db import models
import registration.models
from django.db.models import SET
from django.db.models.signals import post_save
from notifications.signals import notify


class Message(models.Model):
    class Meta:
        permissions = (
                       ("process_message", "Can view and process users messages"),
                       )
    receiver_user = models.ForeignKey(registration.models.User, related_name='receiver',
                                      on_delete=SET(AnonymousUser.id))
    sender_user = models.ForeignKey(registration.models.User, related_name='sender',
                                    on_delete=SET(AnonymousUser.id))
    message = models.TextField()
    time = models.DateTimeField(auto_now_add=True)


def my_handler(sender, instance, created, **kwargs):
    notify.send(actor=instance.sender_user, recipient=instance.receiver_user,
                description='You have new message from {}'.format(instance.sender_user))


post_save.connect(my_handler, sender=Message)


class Room(models.Model):
    name = models.CharField(max_length=255, unique=True)
    receiver_user = models.ForeignKey(registration.models.User, related_name='room_receiver',
                                      on_delete=SET(AnonymousUser.id))
    sender_user = models.ForeignKey(registration.models.User, related_name='room_sender',
                                    on_delete=SET(AnonymousUser.id))

    def __str__(self):
        return self.name
