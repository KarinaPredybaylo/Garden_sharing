import registration.models
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.models import Permission
from django.db.models import Q
from django.shortcuts import render, redirect, get_object_or_404
from django.utils.crypto import get_random_string
from django.views import View
from .models import Room, Message

perm = Permission.objects.get(codename='process_message')


class GetAllUsers(LoginRequiredMixin, View):
    def get(self, request):
        users = registration.models.User.objects.all()
        return render(request, 'all_users.html', {'users': users})

    def post(self, request):
        sender = request.user.id
        sender_user = registration.models.User.objects.get(id=sender)
        if sender_user.has_perm('chat.process_message'):
            receiver = request.POST['users']
        else:
            receiver_obj = registration.models.User.objects.filter(user_permissions=perm).first()
            receiver = receiver_obj.id
        receiver_user = registration.models.User.objects.get(id=receiver)
        request.session['receiver_user'] = receiver
        get_room = Room.objects.filter(Q(sender_user=sender_user, receiver_user=receiver_user)
                                       | Q(sender_user=receiver_user, receiver_user=sender_user))
        if get_room:
            room_name = get_room[0].name
        else:
            new_room = get_random_string(5)

            while True:
                room_exists = Room.objects.filter(name=new_room)
                if room_exists:
                    new_room = get_random_string(5)
                else:
                    break
            create_room = Room.objects.create(sender_user=sender_user, receiver_user=receiver_user, name=new_room)
            create_room.save()
            room_name = create_room.name
        return redirect('room', room_name=room_name)


class ChatRoom(LoginRequiredMixin, View):
    queryset = Room.objects.all()

    def get(self, request, room_name, *args, **kwargs):
        get_object_or_404(Room, name=self.kwargs.get('room_name'))
        room = Room.objects.get(name=self.kwargs.get('room_name'))
        sender = request.user.id
        sender_name = registration.models.User.objects.get(id=sender).username

        if room.receiver_user.id == sender:
            receiver = room.sender_user.id
        else:
            receiver = room.receiver_user.id
        messages = Message.objects.filter(Q(sender_user=sender,
                                            receiver_user=receiver) |
                                          Q(sender_user=receiver, receiver_user=sender)).order_by('time')
        context = {'room_name': room_name,
                   'sender_id': sender,
                   'receiver_id': receiver,
                   'messages': messages,
                   'sender_name': sender_name}
        return render(request, 'chat.html', context)

# @login_required
# def room(request, room_name):
#     context = {'room_name': room_name}
#     return render(request, "chat.html", context)
