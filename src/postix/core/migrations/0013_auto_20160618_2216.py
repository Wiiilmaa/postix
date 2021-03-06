# -*- coding: utf-8 -*-
# Generated by Django 1.9.6 on 2016-06-18 20:16
from __future__ import unicode_literals

import django.db.models.deletion
import django.utils.timezone
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [("core", "0012_auto_20160601_1833")]

    operations = [
        migrations.AddField(
            model_name="itemmovement",
            name="backoffice_user",
            field=models.ForeignKey(
                default=1,
                on_delete=django.db.models.deletion.PROTECT,
                related_name="supervised_item_movements",
                to=settings.AUTH_USER_MODEL,
                verbose_name="Backoffice operator issuing movement",
            ),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name="cashdesksession",
            name="cashdesk",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.PROTECT,
                related_name="sessions",
                to="core.Cashdesk",
            ),
        ),
        migrations.AlterField(
            model_name="itemmovement",
            name="timestamp",
            field=models.DateTimeField(
                default=django.utils.timezone.now, editable=False
            ),
        ),
    ]
