# Generated by Django 2.1.4 on 2018-12-27 08:07

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [("core", "0059_auto_20181226_1110")]

    operations = [
        migrations.AlterField(
            model_name="productitem", name="amount", field=models.IntegerField()
        )
    ]
