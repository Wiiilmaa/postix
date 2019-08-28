# Generated by Django 2.1.2 on 2018-10-18 22:12

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [("core", "0047_auto_20180610_1431")]

    operations = [
        migrations.AlterField(
            model_name="record",
            name="backoffice_user",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.PROTECT,
                related_name="records",
                to=settings.AUTH_USER_MODEL,
                verbose_name="Backoffice user",
            ),
        )
    ]
