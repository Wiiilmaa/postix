# -*- coding: utf-8 -*-
# Generated by Django 1.9.6 on 2016-11-14 21:40
from __future__ import unicode_literals

import django.utils.timezone
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [("core", "0025_auto_20161102_1659")]

    operations = [
        migrations.AlterField(
            model_name="cashdesksession",
            name="start",
            field=models.DateTimeField(
                default=django.utils.timezone.now,
                help_text="Default: time of creation.",
                verbose_name="Start of session",
            ),
        )
    ]
