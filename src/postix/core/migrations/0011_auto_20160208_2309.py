# -*- coding: utf-8 -*-
# Generated by Django 1.9.2 on 2016-02-08 22:09
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [("core", "0010_auto_20160208_2309")]

    operations = [
        migrations.AddField(
            model_name="listconstraint",
            name="products",
            field=models.ManyToManyField(
                blank=True,
                through="core.ListConstraintProduct",
                to="core.Product",
                verbose_name="Affected products",
            ),
        ),
        migrations.AddField(
            model_name="warningconstraint",
            name="products",
            field=models.ManyToManyField(
                blank=True,
                through="core.WarningConstraintProduct",
                to="core.Product",
                verbose_name="Affected products",
            ),
        ),
    ]
