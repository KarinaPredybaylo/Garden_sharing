# Generated by Django 4.0.8 on 2022-10-31 13:44

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('sharing', '0002_request_address_request_city'),
    ]

    operations = [
        migrations.AddField(
            model_name='request',
            name='phone',
            field=models.CharField(blank=True, default='', max_length=50),
        ),
    ]
