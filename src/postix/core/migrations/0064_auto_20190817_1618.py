# Generated by Django 2.1.4 on 2019-08-17 14:18

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0063_auto_20190817_1453'),
    ]

    operations = [
        migrations.AddField(
            model_name='preorder',
            name='is_canceled',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='preorderposition',
            name='price',
            field=models.DecimalField(decimal_places=2, max_digits=10, null=True, blank=True),
        ),
    ]
