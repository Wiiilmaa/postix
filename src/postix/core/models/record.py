from django.conf import settings
from django.db import models
from django.utils.timezone import now
from django.utils.translation import ugettext_lazy as _


class RecordEntity(models.Model):
    """ This class is the source or destination for records, for example "Bar 1", or "Unnamed Supplier" """
    name = models.CharField(max_length=200, help_text='For example "Bar", or "Vereinstisch", …')
    detail = models.CharField(max_length=200, help_text='For example the name of the bar, …')

    class Meta:
        ordering = ('name', 'detail')

    def __str__(self):
        return '{s.name}: {s.detail}'.format(s=self)


class Record(models.Model):
    TYPES = (
        ('inflow', _('Inflow')),
        ('outflow', _('Outflow')),
    )
    type = models.CharField(max_length=20, choices=TYPES, verbose_name=_('Direction'))
    datetime = models.DateTimeField(verbose_name=_('Date'), help_text=_('Leave empty to use the current date and time.'))
    entity = models.ForeignKey(RecordEntity, on_delete=models.PROTECT, related_name='records', verbose_name=_('Entity'), null=True, blank=True)
    carrier = models.CharField(max_length=200, null=True, blank=True, verbose_name=_('Carrier'))
    amount = models.DecimalField(decimal_places=2, max_digits=10, verbose_name=_('Amount'))
    backoffice_user = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='records', verbose_name=_('Backoffice user'))
    is_balancing = models.BooleanField(default=False, verbose_name=_('Is a balancing record'))

    class Meta:
        ordering = ('datetime', )

    def __str__(self):
        return self.datetime.strftime('Day %d %X') + " " + str(self.entity) + " " + str(self.amount) + " EUR"
        
    def save(self, *args, **kwargs):
        if not self.datetime:
            self.datetime = now()
        super().save(*args, **kwargs)
