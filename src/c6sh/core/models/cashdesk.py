import random
import string

from django.db import models
from django.utils.timezone import now

from .base import Item


def generate_key():
    return "".join(random.choice(string.ascii_letters + string.digits) for i in range(32))


class Cashdesk(models.Model):
    name = models.CharField(max_length=254)
    ip_address = models.GenericIPAddressField(unique=True, verbose_name='IP address')
    printer_queue_name = models.CharField(max_length=254, null=True, blank=True,
                                          verbose_name='Printer queue name')
    display_address = models.GenericIPAddressField(null=True, blank=True,
                                                   verbose_name='Display IP address')
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.name

    def get_active_sessions(self):
        return [session for session in self.sessions.all() if session.is_active()]


class CashdeskSession(models.Model):
    cashdesk = models.ForeignKey('Cashdesk', related_name='sessions', on_delete=models.PROTECT)
    user = models.ForeignKey('User', on_delete=models.PROTECT)
    start = models.DateTimeField(null=True, blank=True,
                                 verbose_name='Start of session',
                                 help_text='Automatically set on first login')
    end = models.DateTimeField(null=True, blank=True,
                               verbose_name='End of session',
                               help_text='Only set if session has ended')
    cash_before = models.DecimalField(max_digits=10, decimal_places=2,
                                      verbose_name='Cash in drawer before session')
    cash_after = models.DecimalField(max_digits=10, decimal_places=2,
                                     null=True, blank=True,
                                     verbose_name='Cash in drawer after session')
    backoffice_user_before = models.ForeignKey('User', on_delete=models.PROTECT,
                                               related_name='supervised_session_starts',
                                               verbose_name='Backoffice operator before session')
    backoffice_user_after = models.ForeignKey('User', on_delete=models.PROTECT,
                                              null=True, blank=True,
                                              related_name='supervised_session_ends',
                                              verbose_name='Backoffice operator after session')
    api_token = models.CharField(max_length=254, default=generate_key,
                                 verbose_name='API token',
                                 help_text='Used for non-browser sessions. Generated automatically.')
    comment = models.TextField(blank=True)

    def __str__(self):
        return '#{2} ({0} on {1})'.format(self.user, self.cashdesk, self.pk)

    def is_active(self):
        return (not self.start or self.start < now()) and not self.end

    def get_current_items(self):
        # TODO FIXME this only gives the amount of items entered/removed via an ItemMovement
        # we completely disregard transactions for now, because testing those is hard. will come later
        return [{'item': Item.objects.get(pk=d['item']), 'total': d['total']} \
                for d in self.item_movements.values('item').annotate(total=models.Sum('amount'))]


class ItemMovement(models.Model):
    """ Instead of a through-table. Negative amounts indicate items moved out
    of a session, this mostly happens when a session is closed and all remaining
    items are removed and counted manually. """
    session = models.ForeignKey('CashdeskSession', on_delete=models.PROTECT,
                                related_name='item_movements',
                                verbose_name='Session the item was involved in')
    item = models.ForeignKey('Item', on_delete=models.PROTECT,
                             related_name='item_movements',
                             verbose_name='Item moved to/from this session')
    amount = models.IntegerField(help_text='Negative values indicate that items were taken out of a session. '
                                           'Mostly used when counting items after ending a session.')
    timestamp = models.DateTimeField(default=now(), editable=False)
