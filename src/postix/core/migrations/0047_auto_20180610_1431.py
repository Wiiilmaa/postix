# -*- coding: utf-8 -*-
# Generated by Django 1.11.8 on 2018-06-10 12:31
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [("core", "0046_auto_20180610_1405")]

    operations = [
        migrations.AlterModelOptions(name="record", options={"ordering": ("datetime",)})
    ]
