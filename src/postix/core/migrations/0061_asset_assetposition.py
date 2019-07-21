# Generated by Django 2.1.9 on 2019-07-21 13:46

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0060_auto_20181227_0907'),
    ]

    operations = [
        migrations.CreateModel(
            name='Asset',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('identifier', models.CharField(max_length=190, unique=True)),
                ('asset_type', models.CharField(choices=[('box', 'box'), ('inlay', 'inlay'), ('bag', 'bag'), ('counting_board', 'counting_board')], max_length=190)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('last_seen', models.DateTimeField(auto_now_add=True)),
            ],
        ),
        migrations.CreateModel(
            name='AssetPosition',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('start', models.DateTimeField(auto_now_add=True)),
                ('end', models.DateTimeField(blank=True, null=True)),
                ('location', models.CharField(max_length=190)),
                ('comment', models.CharField(max_length=190, null=True)),
                ('asset', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='positions', to='core.Asset')),
            ],
        ),
    ]
