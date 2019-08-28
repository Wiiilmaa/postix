# -*- coding: utf-8 -*-
# Generated by Django 1.9.2 on 2016-02-07 09:45
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [("core", "0003_auto_20160206_2052")]

    operations = [
        migrations.CreateModel(
            name="WarningConstraint",
            fields=[
                (
                    "id",
                    models.AutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("name", models.CharField(max_length=254)),
                ("message", models.TextField()),
                (
                    "products",
                    models.ManyToManyField(
                        blank=True, to="core.Product", verbose_name="Affected products"
                    ),
                ),
            ],
            options={"abstract": False},
        )
    ]
