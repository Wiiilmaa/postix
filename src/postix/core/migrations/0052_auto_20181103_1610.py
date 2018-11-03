# Generated by Django 2.1.3 on 2018-11-03 15:10

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0051_auto_20181103_1516'),
    ]

    operations = [
        migrations.AlterField(
            model_name='cashdesksession',
            name='user',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, to=settings.AUTH_USER_MODEL),
        ),
    ]