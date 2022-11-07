from django.urls import path

from . import views

urlpatterns = [path("rooms/<str:room_name>/", views.ChatRoom.as_view(), name="room"),
               path('rooms/', views.GetAllUsers.as_view(), name='rooms')]
