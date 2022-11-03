import json

from celery import shared_task
from celery.utils.log import get_task_logger

from django.core.mail import EmailMessage
from django.template.loader import render_to_string
import garden_sharing.settings

logger = get_task_logger(__name__)


@shared_task(name='my_first_task')
def send_email_update(domain, users, template='we_have_good_for_you.html', things=None):
    users = json.loads(users)
    for user in users:
        print([user['email']])
        context = {
            'user': user,
            'domain': domain,
            'things': things
        }
        message = render_to_string(
            template,
            context=context,
        )

        email = EmailMessage(
            template,
            message,
            from_email=garden_sharing.settings.EMAIL_HOST_USER,
            to=[user['email']],
        )
        email.send()

# def my_first_task(duration):
#     is_task_completed= False
#     error=''
#     try:
#         sleep(duration)
#         is_task_completed = True
#     except Exception as err:
#         error = str(err)
#         logger.error(error)
#     if is_task_completed:
#         send_email_update(request, user=request.user)
#     else:
#         send_mail_to(subject, error, receivers)
#     return('first_task_done')
