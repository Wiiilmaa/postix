# Generated by Django 2.1.3 on 2018-12-07 13:04

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0055_ping_synced'),
    ]

    operations = [
        migrations.AddField(
            model_name='eventsettings',
            name='queue_sync_token',
            field=models.CharField(blank=True, max_length=100, null=True, verbose_name='c3queue authentication token'),
        ),
        migrations.AddField(
            model_name='eventsettings',
            name='queue_sync_url',
            field=models.URLField(blank=True, default='https://c3queue.de', help_text='The URL of the c3queue.de instance', max_length=100, null=True, verbose_name='c3queue.de URL'),
        ),
    ]
