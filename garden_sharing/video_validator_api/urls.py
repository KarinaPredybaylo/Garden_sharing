from django.urls import re_path
import video_validator_api.views

app_name = 'video_validator_api'


urlpatterns = [
    re_path(r'^create_video$', video_validator_api.views.VideoAPIView.as_view()),
    re_path(r'^plant/(?P<plant_id>[\d-]+)/video/(?P<video_id>[\d-]+)$',
            video_validator_api.views.FileUploadObject.as_view())
]
