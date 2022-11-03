from django.contrib.sites.shortcuts import get_current_site
from django.core.mail import EmailMessage
from django.template.loader import render_to_string
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode
from django.contrib.auth.tokens import default_token_generator as \
 token_generator


def send_email(request, user, template='verify_email.html'):
    current_site = get_current_site(request)
    context = {
        'user': user,
        'domain': current_site.domain,
        'uid': urlsafe_base64_encode(force_bytes(user.pk)),
        'token': token_generator.make_token(user),
    }
    message = render_to_string(
        template,
        context=context,
    )
    from Plants_share.garden_sharing.garden_sharing import settings
    email = EmailMessage(
        template,
        message,
        from_email=settings.EMAIL_HOST_USER,
        to=[user.email],
    )
    email.send()
