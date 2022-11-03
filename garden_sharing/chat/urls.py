from django.urls import path
from django.views.generic import TemplateView

from . import views

urlpatterns = [path("rooms/<str:room_name>/", views.ChatRoom.as_view(), name="room"),
               # path('', TemplateView.as_view(template_name='chat_rooms.html'), name='chat_rooms'),
               path('rooms/', views.GetAllUsers.as_view(), name='rooms')]
