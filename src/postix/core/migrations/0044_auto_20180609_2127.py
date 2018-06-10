# -*- coding: utf-8 -*-
# Generated by Django 1.11.8 on 2018-06-09 19:27
from __future__ import unicode_literals

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0043_auto_20180101_1525'),
    ]

    operations = [
        migrations.CreateModel(
            name='Record',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('type', models.CharField(choices=[('inflow', 'inflow'), ('outflow', 'outflow')], max_length=20)),
                ('datetime', models.DateTimeField(auto_now_add=True)),
                ('carrier', models.CharField(blank=True, max_length=200, null=True)),
                ('amount', models.DecimalField(decimal_places=2, max_digits=10)),
                ('is_balancing', models.BooleanField(default=False)),
                ('backoffice_user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='records', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='RecordEntity',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(help_text='For example "Bar", or "Vereinstisch", …', max_length=200)),
                ('detail', models.CharField(help_text='For example the name of the bar, …', max_length=200)),
            ],
        ),
        migrations.AlterField(
            model_name='cashdesk',
            name='printer_handles_drawer',
            field=models.BooleanField(default=True, help_text='Ausschalten, wenn Drucker oder Schublade kaputt sind.', verbose_name='Drucker steuert Schublade'),
        ),
        migrations.AddField(
            model_name='record',
            name='entity',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='records', to='core.RecordEntity'),
        ),
    ]