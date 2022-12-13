import os
from celery import Celery
from celery.schedules import crontab
from django.conf import settings
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'garden_sharing.settings')
app = Celery('garden_sharing')
app.config_from_object(settings, namespace='CELERY')
app.conf.beat_schedule = {
    'generate_sound-every-day': {
        'task': 'video_validator_api.tasks.generate_tone',
        'schedule': crontab(minute=0, hour=0)
        # 'args': '..'
    },
}

app.autodiscover_tasks(lambda: settings.INSTALLED_APPS)

@app.task(bind=True)
def debug_task(self):
    print('Request: {0!r}'.format(self.request))
