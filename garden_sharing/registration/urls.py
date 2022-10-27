from django.urls import re_path, path
from django.views.generic import TemplateView

from . import views
from django.contrib.auth import views as auth_views

from .views import EmailVerify, LoginView

urlpatterns = [
    re_path(r'^$', views.register, name='register'),
    path('profile/', views.profile, name='profile'),
    path('confrim/', TemplateView.as_view(template_name='confirm_email.html'), name='confirm_email'),
    path('verify_email/<uidb64>/<token>/', EmailVerify.as_view(), name='verify_email'),
    path('invalid_verify/', TemplateView.as_view(template_name='incorrect_email.html', ), name='incorrect_email'),
    path('login/', LoginView.as_view(template_name='login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(template_name='index.html'), name='logout'),
]
