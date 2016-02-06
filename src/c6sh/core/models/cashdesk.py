import random
import string

from django.contrib.auth.base_user import AbstractBaseUser, BaseUserManager
from django.db import models


def generate_key():
    return "".join(random.choice(string.ascii_letters + string.digits) for i in range(32))


class Cashdesk(models.Model):
    name = models.CharField(max_length=254)
    ip_address = models.GenericIPAddressField(unique=True)
    printer_queue_name = models.CharField(max_length=254, null=True, blank=True)
    display_address = models.GenericIPAddressField(null=True, blank=True)
    is_active = models.BooleanField(default=True)


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
