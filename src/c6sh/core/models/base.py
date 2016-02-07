from django.db import models
from django.db.models import Q
from django.utils import timezone

from ..utils import round_decimal


class Transaction(models.Model):
    datetime = models.DateTimeField(auto_now_add=True)
    cash_given = models.DecimalField(null=True, max_digits=10, decimal_places=2)
    session = models.ForeignKey('CashdeskSession', related_name='transactions',
                                on_delete=models.PROTECT)


class TransactionPosition(models.Model):
    TYPES = (
        ('redeem', 'Presale redemption'),
        ('reverse', 'Reversal'),
        ('sell', 'Sale')
    )

    transaction = models.ForeignKey('Transaction', related_name='positions',
                                    on_delete=models.PROTECT)
    type = models.CharField(choices=TYPES, max_length=100)
    value = models.DecimalField(max_digits=10, decimal_places=2)
    tax_rate = models.DecimalField(max_digits=4, decimal_places=2)
    tax_value = models.DecimalField(max_digits=10, decimal_places=2)
    product = models.ForeignKey('Product', related_name='positions',
                                on_delete=models.PROTECT)
    reverses = models.ForeignKey('TransactionPosition', related_name='reversed_by',
                                 on_delete=models.PROTECT, null=True, blank=True)
    listentry = models.ForeignKey('ListConstraintEntry', related_name='positions',
                                  on_delete=models.PROTECT, null=True, blank=True)
    preorder_position = models.ForeignKey('PreorderPosition', related_name='transaction_positions',
                                          on_delete=models.PROTECT, null=True, blank=True)
    items = models.ManyToManyField('Item', through='TransactionPositionItem',
                                   blank=True)
    authorized_by = models.ForeignKey('User', null=True, blank=True, on_delete=models.PROTECT,
                                      related_name='authorized')

    def save(self, *args, **kwargs):
        if not self.value:
            self.value = self.product.price
        if not self.tax_rate:
            self.tax_rate = self.product.tax_rate
        if not self.tax_value:
            net_value = self.value * 100 / (100 + self.tax_rate)
            self.tax_value = round_decimal(self.value - net_value)
        super(TransactionPosition, self).save(*args, **kwargs)
        if not self.items.exists():
            for pi in self.product.product_items.all().select_related('item'):
                TransactionPositionItem.objects.create(
                    position=self, item=pi.item, amount=pi.amount
                )

    def was_reversed(self):
        if self.type == 'reverse':
            return False

        return TransactionPosition.objects.filter(reverses=self, type='reverse').exists()


class Product(models.Model):
    name = models.CharField(max_length=254)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    tax_rate = models.DecimalField(max_digits=4, decimal_places=2,
                                   verbose_name='Tax rate',
                                   help_text='in percent')
    is_visible = models.BooleanField(default=True)
    requires_authorization = models.BooleanField(default=False)
    items = models.ManyToManyField('Item', through='ProductItem', blank=True)

    def is_available(self):
        from .models import Quota, TimeConstraint
        timeframes = TimeConstraint.objects.filter(products=self)
        if timeframes.exists():
            now = timezone.now()
            current_timeframes = timeframes.filter(start__lte=now, end__gte=now)
            if not current_timeframes.exists():
                return False

        quotas = Quota.objects.filter(products=self)
        if quotas.exists():
            all_quotas_available = all([quota.is_available() for quota in quotas])
            if not all_quotas_available:
                return False

        return True

    def amount_sold(self):
        positions = self.transactionposition_set.filter(Q(type='redeem') | Q(type='sell'))
        valid_positions = [position for position in positions if not position.was_reversed]
        return len(valid_positions)

    def __str__(self):
        return self.name


class Item(models.Model):
    name = models.CharField(max_length=254)
    description = models.TextField(blank=True)
    initial_stock = models.PositiveIntegerField()

    def __str__(self):
        return self.name


class ProductItem(models.Model):
    product = models.ForeignKey('Product', on_delete=models.PROTECT,
                                related_name='product_items')
    item = models.ForeignKey('Item', on_delete=models.PROTECT,
                             related_name='product_items')
    amount = models.PositiveIntegerField()


class TransactionPositionItem(models.Model):
    position = models.ForeignKey('TransactionPosition', on_delete=models.PROTECT,
                                 related_name='transaction_position_items')
    item = models.ForeignKey('Item', on_delete=models.PROTECT,
                             related_name='transaction_position_items')
    amount = models.PositiveIntegerField()
