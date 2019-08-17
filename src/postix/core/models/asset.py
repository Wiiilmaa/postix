from django.db import models
from django.utils.translation import ugettext_lazy as _


class Asset(models.Model):
    ASSET_TYPE = (
        ('box', _('Box')),
        ('inlay', _('Inlay')),
        ('bag', _('Bag')),
        ('counting_board', _('Counting board')),
    )
    identifier = models.CharField(max_length=190, unique=True)
    asset_type = models.CharField(
        max_length=190,
        choices=ASSET_TYPE
    )
    description = models.CharField(max_length=190)
    created = models.DateTimeField(auto_now_add=True)
    last_seen = models.DateTimeField()

    def get_current_position(self):
        return self.positions.filter(end__isnull=True).order_by('start').first()


class AssetPosition(models.Model):
    asset = models.ForeignKey(
        Asset,
        related_name='positions',
        on_delete=models.PROTECT
    )
    start = models.DateTimeField()
    end = models.DateTimeField(null=True, blank=True)
    location = models.CharField(max_length=190)
    comment = models.CharField(max_length=190, null=True)
