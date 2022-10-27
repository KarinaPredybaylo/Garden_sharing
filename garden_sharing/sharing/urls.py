from django.urls import re_path, path
from django.views.generic import TemplateView

from . import views
from .views import PlantDetailView, ToolDetailView

urlpatterns = [
    re_path(r'^$', views.home_page, name='home'),
    path('request', TemplateView.as_view(template_name='request.html'), name='request'),
    path('request_detail', views.request_detail, name='request_detail'),
    path('request_success', views.request_success, name='request_success'),
    path('requestthing_list', views.RequestView.as_view(), name='request_list'),
    path('share', TemplateView.as_view(template_name='share.html'), name='share'),
    path('no_place', TemplateView.as_view(template_name='no_place.html'), name='no_place'),
    path('share_detail', views.share_detail, name='share_detail'),
    path('share_success', views.share_success, name='share_success'),
    path('set_office', views.set_city_session, name='set_session_city'),
    path('share_list', views.share_list, name='share_list'),
    path('share/<pk>', views.share_update, name='share_update'),
    path('tool_list', views.sharing_things, name='tools_list'),
    path('plant_list', views.sharing_plants, name='plants_list'),
    path('plant/<pk>', PlantDetailView.as_view(), name='plant_detail'),
    path('tool/<pk>', ToolDetailView.as_view(), name='tool_detail'),
    path('requestthing_list', views.request_list, name='missing_request_thing'),
    path('sharething_list', views.sharing_list, name='able_share_thing'),
              ]
