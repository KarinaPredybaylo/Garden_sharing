from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils.translation import gettext_lazy as _


class User(AbstractUser):
    email = models.EmailField(
        _('email address'),
        unique=True,
    )

    email_verify = models.BooleanField(default=False)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    photo = models.ImageField(default='default.png', upload_to='profile_images')
    # email_verify = models.BooleanField(default=False, blank=True)

    def __str__(self):
        return f'{self.user.username} Profile'


def create_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)
        instance.profile.save()


models.signals.post_save.connect(receiver=create_profile, sender=User)
