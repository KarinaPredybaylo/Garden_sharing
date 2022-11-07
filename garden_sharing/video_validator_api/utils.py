import os
import moviepy.editor as mp
import wave
import datetime
import garden_sharing.settings
import ffmpeg
import librosa
import soundfile
import video_validator_api.views
from rest_framework.exceptions import APIException
from rest_framework.views import exception_handler


def write_audio(video_path, output_path,
                audio_path=garden_sharing.settings.MEDIA_ROOT + '/audio/date.wav'
                ):

    with wave.open(audio_path, 'rb') as q:
        len_frame = q.getnframes()
        rate = q.getframerate()

    video = ffmpeg.input(video_path).video
    audio = ffmpeg.input(audio_path).audio
    path = garden_sharing.settings.MEDIA_ROOT + '/videos_uploaded/' + output_path
    output = ffmpeg.output(video, audio, path, vcodec='copy', acodec='aac', strict='experimental')
    result = '/videos_uploaded/' + output_path
    ffmpeg.run(output)
    os.remove(video_path)
    return result, len_frame, rate


data = datetime.date.today()
day = int(data.strftime("%d"))
month = int(data.strftime("%m"))
year = int(data.strftime("%Y"))


def convert_video_to_audio_wav(video_file, rate, frames):
    duration = frames / rate
    my_clip = mp.VideoFileClip(video_validator_api.views.path_p + video_file)
    clip = my_clip.subclip(0, duration)
    clip.audio.write_audiofile(garden_sharing.settings.MEDIA_ROOT + '/audio/result.mp3')
    file_in = garden_sharing.settings.MEDIA_ROOT + '/audio/result.mp3'
    file_out = garden_sharing.settings.MEDIA_ROOT + '/audio/result.wav'
    os.system("lame -b320 %s %s" % (file_in, file_out))
    os.remove(file_in)
    x, _ = librosa.load(file_out, sr=int(rate))
    soundfile.write(file_out, x, int(rate))
    return file_out


def video_validate(video, rate, frames):
    print(frames)
    audio = convert_video_to_audio_wav(video, rate, frames)
    with wave.open(audio, 'rb') as actual:
        len_frame_today = actual.getnframes()
        actual_audio = actual.readframes(len_frame_today)
        rate_today = actual.getframerate()
        (print(len_frame_today, rate_today))

    with wave.open(garden_sharing.settings.MEDIA_ROOT + '/audio/result.wav', 'rb') as added:
        len_frame_audio = added.getnframes()
        added_audio = added.readframes(len_frame_audio)
        rate_audio = added.getframerate()
        (print(len_frame_audio, rate_audio))

    if len_frame_today == len_frame_audio and rate_today == rate_audio:

        actual_list = []
        for i in actual_audio:
            actual_list.append(i)

        added_list = []
        for k in added_audio:
            added_list.append(k)

        check = all(item in added_list for item in actual_list)
        print(check, len(added_list), len(actual_list))
        if check is True:
            return True
        else:
            return False
    else:
        return False


class VideoException(APIException):
    status_code = 503
    default_detail = 'Unable to add video: video is not actual, please, make a new video and add it'
    default_code = '4026'


def custom_exception_handler(exc, context):
    response = exception_handler(exc, context)

    if response is not None:
        response.data['status_code'] = '4026'

    return response
