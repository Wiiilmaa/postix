# -*- coding: utf-8 -*-
# Generated by Django 1.9.6 on 2016-11-23 17:52
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0026_auto_20161114_2240'),
    ]

    operations = [
        migrations.AddField(
            model_name='eventsettings',
            name='initialized',
            field=models.BooleanField(default=False),
        ),
    ]