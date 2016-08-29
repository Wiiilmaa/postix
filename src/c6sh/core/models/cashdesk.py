import glob
import os
import random
import string

from django.core.files.storage import default_storage
from django.db import models
from django.utils.timezone import now

from ..utils.printing import CashdeskPrinter, DummyPrinter
from .base import Item, Product, TransactionPosition, TransactionPositionItem
from .settings import EventSettings


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

    @property
    def printer(self):
        if self.printer_queue_name:
            return CashdeskPrinter(self.printer_queue_name)
        return DummyPrinter()

    def get_active_sessions(self):
        return [session for session in self.sessions.filter(end__isnull=True) if session.is_active()]


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

    def get_item_set(self):
        return [Item.objects.get(pk=pk)
                for pk in self.item_movements.order_by().values_list('item', flat=True).distinct()]

    def get_current_items(self):
        transactions = TransactionPositionItem.objects\
            .values('item')\
            .filter(position__transaction__session=self)\
            .exclude(position__type='reverse')\
            .filter(position__reversed_by=None)\
            .annotate(total=models.Sum('amount'))
        item_movements = self.item_movements\
            .values('item')\
            .annotate(total=models.Sum('amount'))

        post_movement_dict = {}
        if self.end:
            post_movements = item_movements.filter(timestamp__gte=self.end)
            item_movements = item_movements.filter(timestamp__lt=self.end)
            post_movement_dict = {d['item']: {'total': d['total']} for d in post_movements}
        movement_dict = {d['item']: {'total': d['total']} for d in item_movements}
        transaction_dict = {d['item']: {'total': d['total']} for d in transactions}

        DEFAULT = {'total': 0}
        return [{
            'item': item,
            'movements': movement_dict.get(item.pk, DEFAULT)['total'],
            'transactions': transaction_dict.get(item.pk, DEFAULT)['total'],
            'final_movements': -post_movement_dict.get(item.pk, DEFAULT)['total'] if self.end else 0,
            'total': movement_dict.get(item.pk, DEFAULT)['total']
                + post_movement_dict.get(item.pk, DEFAULT)['total']
                - transaction_dict.get(item.pk, DEFAULT)['total'],
        } for item in self.get_item_set()]

    def get_cash_transaction_total(self):
        return TransactionPosition.objects\
            .filter(transaction__session=self)\
            .filter(type__in=['sell', 'reverse'])\
            .aggregate(total=models.Sum('value'))['total'] or 0

    def get_product_sales(self):
        qs = TransactionPosition.objects.filter(transaction__session=self)
        result = []

        for p in qs.order_by().values('product').distinct():
            product = Product.objects.get(pk=p['product'])
            product_query = qs.filter(product=product)
            summary = {
                'product': product,
                'sales': product_query.filter(type='sell').count(),
                'presales': product_query.filter(type='redeem').count(),
                'reversals': product_query.filter(type='reverse').count(),
                'value_single': product_query.values_list('value')[0][0],
            }
            summary['value_total'] = (summary['sales'] - summary['reversals']) * summary['value_single']
            result.append(summary)
        return result

    def get_report_path(self):
        base = default_storage.path('reports')
        search = os.path.join(base, '{}_sessionreport_{}-*.pdf'.format(
            EventSettings.objects.get().short_name,
            self.pk)
        )
        all_reports = sorted(glob.glob(search))

        if all_reports:
            return all_reports[-1]
        return None

    def get_new_report_path(self):
        return os.path.join(
            'reports',
            '{}_sessionreport_{}-{}.pdf'.format(
                EventSettings.objects.get().short_name,
                self.pk,
                now().strftime('%Y%m%d-%H%M')
            ),
        )


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
    backoffice_user = models.ForeignKey('User', on_delete=models.PROTECT,
                                        related_name='supervised_item_movements',
                                        verbose_name='Backoffice operator issuing movement')
    timestamp = models.DateTimeField(default=now, editable=False)
