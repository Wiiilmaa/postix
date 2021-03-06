# -*- coding: utf-8 -*-
# Generated by Django 1.9.2 on 2016-08-29 11:47
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [("core", "0017_auto_20160829_1339")]

    operations = [
        migrations.AddField(
            model_name="productitem",
            name="is_visible",
            field=models.BooleanField(
                default=True,
                help_text="If activated, this item will be shown in the frontend",
            ),
        )
    ]
