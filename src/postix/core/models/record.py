import glob
import hashlib
import os

from django.conf import settings
from django.core.files.storage import default_storage
from django.db import models
from django.utils.timezone import now
from django.utils.translation import ugettext_lazy as _

from .settings import EventSettings


def record_balance():
    balance = 0
    for record in Record.objects.all():
        if record.type == 'inflow':
            balance += record.amount
        elif record.type == 'outflow':
            balance -= record.amount
    return balance


class RecordEntity(models.Model):
    """This class is the source or destination for records, for example "Bar 1", or "Unnamed Supplier"."""

    name = models.CharField(
        max_length=200, help_text='For example "Bar", or "Vereinstisch", …'
    )
    detail = models.CharField(
        max_length=200, help_text='For example the name of the bar, …'
    )

    class Meta:
        ordering = ('name', 'detail')

    def __str__(self):
        return '{s.name}: {s.detail}'.format(s=self)


class Record(models.Model):
    TYPES = (('inflow', _('Inflow')), ('outflow', _('Outflow')))
    type = models.CharField(max_length=20, choices=TYPES, verbose_name=_('Direction'))
    datetime = models.DateTimeField(
        verbose_name=_('Date'),
        help_text=_('Leave empty to use the current date and time.'),
    )
    cash_movement = models.OneToOneField(
        to='core.CashMovement',
        on_delete=models.SET_NULL,
        related_name='record',
        null=True,
        blank=True,
    )
    entity = models.ForeignKey(
        RecordEntity,
        on_delete=models.PROTECT,
        related_name='records',
        verbose_name=_('Entity'),
        null=True,
        blank=True,
    )
    carrier = models.CharField(
        max_length=200, null=True, blank=True, verbose_name=_('Carrier')
    )
    amount = models.DecimalField(
        decimal_places=2, max_digits=10, verbose_name=_('Amount')
    )
    backoffice_user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name='records',
        verbose_name=_('Backoffice user'),
        on_delete=models.PROTECT,
    )
    is_balancing = models.BooleanField(
        default=False, verbose_name=_('Is a balancing record')
    )
    closes_session = models.BooleanField(
        default=False,
        verbose_name=_('Report closes session and contains additional pages'),
    )
    is_locked = models.BooleanField(default=False)

    @property
    def checksum(self):
        checksum = hashlib.sha1()
        for attribute in ['type', 'datetime', 'cash_movement', 'entity', 'carrier', 'amount', 'is_balancing']:
            checksum.update(str(getattr(self, attribute, '')).encode())
        return checksum.hexdigest()

    class Meta:
        ordering = ('datetime',)

    def __str__(self):
        return (
            self.datetime.strftime('Day %d %X')
            + " "
            + self.named_entity
            + " "
            + str(self.amount)
            + " EUR"
        )

    @property
    def named_entity(self):
        if self.cash_movement:
            return str(self.cash_movement.session.cashdesk)
        return str(self.entity)

    @property
    def tabbed_entity(self):
        if self.cash_movement:
            return self.cash_movement.session.tabbed_entity
        return '{e.name}\t{e.detail}'.format(e=self.entity)

    @property
    def named_carrier(self):
        if self.cash_movement and self.cash_movement.session.user:
            return str(self.cash_movement.session.user.get_full_name())
        return self.carrier or ''

    def save(self, *args, **kwargs):
        if not self.datetime:
            self.datetime = now()
        super().save(*args, **kwargs)

    @property
    def record_path(self):
        base = default_storage.path('records')
        search = os.path.join(
            base,
            '{}_record_{}-*.pdf'.format(EventSettings.get_solo().short_name, self.pk),
        )
        all_records = sorted(glob.glob(search))

        if all_records:
            return all_records[-1]

    def get_new_record_path(self) -> str:
        return os.path.join(
            'records',
            '{}_record_{}-{}.pdf'.format(
                EventSettings.objects.get().short_name,
                self.pk,
                now().strftime('%Y%m%d-%H%M'),
            ),
        )
