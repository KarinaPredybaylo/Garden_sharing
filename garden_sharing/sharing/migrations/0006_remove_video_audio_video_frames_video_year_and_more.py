# Generated by Django 4.1.3 on 2022-11-06 15:12

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('sharing', '0005_audio_remove_video_duration_remove_video_year_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='video',
            name='audio',
        ),
        migrations.AddField(
            model_name='video',
            name='frames',
            field=models.IntegerField(null=True),
        ),
        migrations.AddField(
            model_name='video',
            name='year',
            field=models.IntegerField(null=True),
        ),
        migrations.DeleteModel(
            name='Audio',
        ),
    ]
