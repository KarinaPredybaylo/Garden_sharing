# Generated by Django 4.1.3 on 2022-11-02 15:48

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('chat', '0003_rename_room_name_room_name'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='message',
            options={'permissions': (('process_message', 'Can view and process users messages'),)},
        ),
    ]
