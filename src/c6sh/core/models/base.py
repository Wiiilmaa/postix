from django.db import models


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
    items = models.ManyToManyField('TransactionPosition', through='TransactionPositionItem')
    authorized_by = models.ForeignKey('User', null=True, blank=True, on_delete=models.PROTECT,
                                      related_name='authorized')


class Product(models.Model):
    name = models.CharField(max_length=254)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    tax_rate = models.DecimalField(max_digits=4, decimal_places=2)
    is_visible = models.BooleanField(default=True)
    requires_authorization = models.BooleanField(default=False)
    items = models.ManyToManyField('Item', through='ProductItem')

    def is_available(self):
        raise NotImplementedError()


class Item(models.Model):
    name = models.CharField(max_length=254)
    description = models.TextField(blank=True)
    initial_stock = models.PositiveIntegerField()


class ProductItem(models.Model):
    product = models.ForeignKey('Product', on_delete=models.PROTECT,
                                related_name='product_items')
    item = models.ForeignKey('Item', on_delete=models.PROTECT,
                             related_name='product_items')
    amount = models.PositiveIntegerField()


class TransactionPositionItem(models.Model):
    product = models.ForeignKey('TransactionPosition', on_delete=models.PROTECT,
                                related_name='transaction_position_items')
    item = models.ForeignKey('Item', on_delete=models.PROTECT,
                             related_name='transaction_position_items')
    amount = models.PositiveIntegerField()
