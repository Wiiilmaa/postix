# Generated by Django 2.1.10 on 2019-08-19 10:51

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [("core", "0064_auto_20190817_1618")]

    operations = [
        migrations.AddField(
            model_name="eventsettings",
            name="maintenance_mode",
            field=models.BooleanField(
                default=False,
                help_text="Block everybody except for superuser users from using the server.",
                verbose_name="Maintenance mode",
            ),
        ),
        migrations.AlterField(
            model_name="asset",
            name="asset_type",
            field=models.CharField(
                choices=[
                    ("box", "Box"),
                    ("inlay", "Inlay"),
                    ("bag", "Bag"),
                    ("counting_board", "Counting board"),
                ],
                max_length=190,
                verbose_name="Type",
            ),
        ),
        migrations.AlterField(
            model_name="asset",
            name="description",
            field=models.CharField(max_length=190, verbose_name="Description"),
        ),
        migrations.AlterField(
            model_name="asset",
            name="identifier",
            field=models.CharField(max_length=190, unique=True, verbose_name="QR code"),
        ),
        migrations.AlterField(
            model_name="cashdesk",
            name="handles_items",
            field=models.BooleanField(default=True, verbose_name="Verteilt Produkte"),
        ),
        migrations.AlterField(
            model_name="cashdesk",
            name="printer_handles_drawer",
            field=models.BooleanField(
                default=True,
                help_text="Ausschalten, wenn Drucker oder Schublade kaputt sind.",
                verbose_name="Drucker steuert Schublade",
            ),
        ),
        migrations.AlterField(
            model_name="cashdesk",
            name="printer_queue_name",
            field=models.CharField(
                blank=True,
                help_text="Der Name, der im CUPS konfiguriert wurde",
                max_length=254,
                null=True,
                verbose_name="Drucker-Name",
            ),
        ),
    ]