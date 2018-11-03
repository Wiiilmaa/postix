# Generated by Django 2.1.3 on 2018-11-03 14:16

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0050_auto_20181103_1452'),
    ]

    operations = [
        migrations.AddField(
            model_name='cashdesk',
            name='record_detail',
            field=models.CharField(blank=True, help_text='For example the name of the bar. Leave empty for presale cashdesks.', max_length=200, null=True),
        ),
        migrations.AddField(
            model_name='cashdesk',
            name='record_name',
            field=models.CharField(blank=True, help_text='For example "Bar", or "Vereinstisch", or "Kassensession"', max_length=200, null=True),
        ),
    ]