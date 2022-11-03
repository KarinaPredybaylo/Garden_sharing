from celery import shared_task
from celery.utils.log import get_task_logger
from django.core.mail import EmailMessage
from django.template.loader import render_to_string
import garden_sharing.settings

logger = get_task_logger(__name__)


@shared_task(name='verify_email')
def send_email(domain, token, uid, name, email, template='verify_email.html'):
    context = {
        'user': name,
        'domain': domain,
        'uid': uid,
        'token': token,
    }
    message = render_to_string(
        template,
        context=context,
    )
    email = EmailMessage(
        template,
        message,
        from_email=garden_sharing.settings.EMAIL_HOST_USER,
        to=[email],
    )
    email.send()
    return "Done"
