# -*- coding: utf-8 -*-
# Generated by Django 1.9.2 on 2016-12-28 10:13
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0034_auto_20161226_1811'),
    ]

    operations = [
        migrations.AddField(
            model_name='preorderposition',
            name='last_transaction',
            field=models.IntegerField(blank=True, null=True),
        ),
    ]
