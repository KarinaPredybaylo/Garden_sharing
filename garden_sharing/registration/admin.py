from django.contrib import admin
from django.contrib.auth import get_user_model
from django.contrib.auth.admin import UserAdmin
from django.utils.safestring import mark_safe

from .models import Profile

User = get_user_model()


@admin.register(User)
class UserAdmin(UserAdmin):
    list_display = ('username', 'email', 'email_verify')
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'email', 'password1', 'password2', 'email_verify'),
        }),
    )


@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ('photo', 'user', 'image')

    def image(self, obj):
        return mark_safe('<img src="{}" width="50"/>'.format(obj.photo.url))

