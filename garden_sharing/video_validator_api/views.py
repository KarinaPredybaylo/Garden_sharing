from rest_framework.parsers import FileUploadParser
from rest_framework import views
from rest_framework.response import Response
import sharing.models
from .utils import write_audio, video_validate, VideoException
import uuid
import garden_sharing.settings

path_p = str(garden_sharing.settings.BASE_DIR)


class VideoAPIView(views.APIView):
    parser_classes = [FileUploadParser]

    def post(self, request):
        video = request.data['file']

        video_obj = sharing.models.Video.objects.create(video=video)
        path = path_p + video_obj.video.url
        filename = str(uuid.uuid4()) + '.mp4'
        new_video, frames, rate = write_audio(video_path=path, output_path=filename)
        video_obj.video = new_video
        video_obj.frames = frames
        video_obj.rate = rate
        video_obj.save()
        return Response(status=200)


class FileUploadObject(views.APIView):

    def put(self, request, plant_id, video_id):
        video_obj = sharing.models.Video.objects.get(pk=video_id)
        video_path = video_obj.video.url
        video_rate = video_obj.rate
        video_frames = video_obj.frames
        plant = sharing.models.Plant.objects.get(pk=plant_id)
        if hasattr(plant, 'video'):
            video_old = plant.video
            video_old.plant = None
            video_old.save()
            if video_validate(video_path, video_rate, video_frames):
                video_obj.plant = plant
                video_obj.save()
                return Response(status=200)
            else:
                raise VideoException()
        else:
            if video_validate(video_path, video_rate, video_frames):
                video_obj.plant = plant
                video_obj.save()
                return Response(status=200)
            else:
                raise VideoException()
