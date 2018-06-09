from django.conf import settings
from django.db import models
from django.utils.timezone import now


class RecordEntity(models.Model):
    """ This class is the source or destination for records, for example "Bar 1", or "Unnamed Supplier" """
    name = models.CharField(max_length=200, help_text='For example "Bar", or "Vereinstisch", …')
    detail = models.CharField(max_length=200, help_text='For example the name of the bar, …')

    def __str__(self):
        return '{s.name}: {s.detail}'.format(s=self)

class Record(models.Model):
    TYPES = (
        ('inflow', 'inflow'),
        ('outflow', 'outflow'),
    )
    type = models.CharField(max_length=20, choices=TYPES)
    datetime = models.DateTimeField()
    entity = models.ForeignKey(RecordEntity, on_delete=models.PROTECT, related_name='records')
    carrier = models.CharField(max_length=200, null=True, blank=True)
    amount = models.DecimalField(decimal_places=2, max_digits=10)
    backoffice_user = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='records')
    is_balancing = models.BooleanField(default=False)

    def __str__(self):
        return self.datetime.strftime('Day %d %X') + " " + str(self.entity) + " " + str(self.amount) + " EUR"
        
    def save(self, *args, **kwargs):
        if not self.datetime:
            self.datetime = now()
        super().save(*args, **kwargs)
