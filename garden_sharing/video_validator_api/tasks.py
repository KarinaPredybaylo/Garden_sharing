import garden_sharing.settings
from celery import shared_task
from celery.utils.log import get_task_logger
import random
import datetime
from tones import SAWTOOTH_WAVE
from tones.mixer import Mixer

notes = {
    "c": 261.625565301,
    "c#": 277.182630977,
    "db": 277.182630977,
    "d": 293.664767918,
    "d#": 311.126983723,
    "eb": 311.126983723,
    "e": 329.627556913,
    "e#": 349.228231433,
    "f": 349.228231433,
    "f#": 369.994422712,
    "gb": 369.994422712,
    "g": 391.995435982,
    "g#": 415.30469758,
    "ab": 415.30469758,
    "a": 440.0,
    "a#": 466.163761518,
    "bb": 466.163761518,
    "b": 493.883301256
}

logger = get_task_logger(__name__)


@shared_task
def generate_tone():
    data = datetime.date.today()
    day = int(data.strftime("%d"))
    month = int(data.strftime("%m"))
    year = int(data.strftime("%Y"))
    mixer = Mixer(year * 20, 1 / 150)
    for i in range(day):
        mixer.create_track(i, SAWTOOTH_WAVE, vibrato_frequency=7.0, vibrato_variance=30.0, attack=0.01, decay=0.1)

    for i in range(month):
        mixer.add_note(0, note=random.choice(list(notes.keys())), octave=4, duration=0.5,
                       endnote=random.choice(list(notes.keys())))

    mixer.write_wav(garden_sharing.settings.MEDIA_ROOT + '/audio/date.wav')
