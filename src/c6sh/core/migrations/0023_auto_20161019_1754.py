# -*- coding: utf-8 -*-
# Generated by Django 1.9.6 on 2016-10-19 15:54
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0022_listconstraint_confidential'),
    ]

    operations = [
        migrations.AddField(
            model_name='eventsettings',
            name='invoice_footer',
            field=models.CharField(blank=True, max_length=200, null=True),
        ),
        migrations.AlterField(
            model_name='eventsettings',
            name='invoice_address',
            field=models.CharField(blank=True, max_length=200, null=True),
        ),
        migrations.AlterField(
            model_name='eventsettings',
            name='receipt_address',
            field=models.CharField(blank=True, max_length=200, null=True),
        ),
        migrations.AlterField(
            model_name='listconstraint',
            name='confidential',
            field=models.BooleanField(default=False, help_text='Confidential lists cannot be shown completely and only searched for substrings longer than 3 letters for a maximum of 10 results.'),
        ),
    ]
