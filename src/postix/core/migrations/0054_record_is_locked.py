# Generated by Django 2.1.3 on 2018-11-03 21:05

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [("core", "0053_auto_20181103_1618")]

    operations = [
        migrations.AddField(
            model_name="record",
            name="is_locked",
            field=models.BooleanField(default=False),
        )
    ]
