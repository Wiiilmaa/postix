import random
import string

from django.contrib.auth.base_user import AbstractBaseUser
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


class AbstractConstraint(models.Model):
    name = models.CharField(max_length=254)
    products = models.ManyToManyField('Product')

    class Meta:
        abstract = True


class Quota(AbstractConstraint):
    size = models.PositiveIntegerField()


class TimeConstraint(AbstractConstraint):
    start = models.DateTimeField(null=True, blank=True)
    end = models.DateTimeField(null=True, blank=True)


class ListConstraint(AbstractConstraint):
    pass


class ListConstraintEntry(models.Model):
    list = models.ForeignKey('ListConstraint', related_name='entries',
                             on_delete=models.PROTECT)
    name = models.CharField(max_length=254)
    identifier = models.CharField(max_length=254)

    def is_redeemed(self):
        raise NotImplementedError()


class Preorder(models.Model):
    order_code = models.CharField(max_length=254, db_index=True)
    is_paid = models.BooleanField(default=False)
    warning_text = models.TextField()


class PreorderPosition(models.Model):
    preorder = models.ForeignKey(Preorder, related_name='positions')
    secret = models.CharField(max_length=254, db_index=True)

    def is_redeemed(self):
        raise NotImplementedError()


class Item(models.Model):
    name = models.CharField(max_length=254)
    description = models.TextField(blank=True)
    initial_stock = models.PositiveIntegerField()


class Cashdesk(models.Model):
    name = models.CharField(max_length=254)
    ip_address = models.GenericIPAddressField()
    printer_queue_name = models.CharField(max_length=254, null=True, blank=True)
    display_address = models.GenericIPAddressField(null=True, blank=True)
    is_active = models.BooleanField(default=True)


def generate_key():
    return "".join(random.choice(string.ascii_letters + string.digits) for i in range(32))


class CashdeskSession(models.Model):
    cashdesk = models.ForeignKey('Cashdesk', on_delete=models.PROTECT)
    user = models.ForeignKey('User', on_delete=models.PROTECT)
    start = models.DateTimeField(null=True, blank=True)
    end = models.DateTimeField(null=True, blank=True)
    cash_before = models.DecimalField(max_digits=10, decimal_places=2)
    cash_after = models.DecimalField(max_digits=10, decimal_places=2,
                                     null=True, blank=True)
    backoffice_user_before = models.ForeignKey('User', on_delete=models.PROTECT,
                                               related_name='supervised_session_starts')
    backoffice_user_after = models.ForeignKey('User', on_delete=models.PROTECT,
                                              null=True, blank=True,
                                              related_name='supervised_session_ends')
    api_token = models.CharField(max_length=254, default=generate_key)
    comment = models.TextField(blank=True)
    items = models.ManyToManyField('Item', through='CashdeskSessionItem')


class CashdeskSessionItem(models.Model):
    session = models.ForeignKey('CashdeskSession', on_delete=models.PROTECT,
                                related_name='cashdesk_session_items')
    item = models.ForeignKey('Item', on_delete=models.PROTECT,
                             related_name='cashdesk_session_items')
    amount_before = models.PositiveIntegerField()
    amount_after = models.PositiveIntegerField(null=True)


class User(AbstractBaseUser):
    username = models.CharField(max_length=254, unique=True)
    firstname = models.CharField(max_length=254)
    lastname = models.CharField(max_length=254)
    is_active = models.BooleanField(default=True)
    is_superuser = models.BooleanField(default=False)
    is_troubleshooter = models.BooleanField(default=False)
    auth_token = models.CharField(max_length=254, null=True, blank=True)

    USERNAME_FIELD = 'username'

    def has_perm(self, perm, obj=None):
        return self.is_superuser

    def has_module_perms(self, app_label):
        return self.is_superuser

    @property
    def is_staff(self):
        return self.is_superuser or self.is_troubleshooter