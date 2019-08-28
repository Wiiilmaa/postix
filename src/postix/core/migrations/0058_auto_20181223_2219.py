# Generated by Django 2.1.3 on 2018-12-23 21:19

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [("core", "0057_itemsupplypack_itemsupplypacklog")]

    operations = [
        migrations.AddField(
            model_name="record",
            name="data",
            field=models.TextField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name="cashdesk",
            name="handles_items",
            field=models.BooleanField(default=True, verbose_name="Handles items"),
        ),
    ]
