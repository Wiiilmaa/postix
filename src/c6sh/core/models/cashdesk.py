import random
import string

from django.contrib.auth.base_user import AbstractBaseUser, BaseUserManager
from django.db import models


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


class CashdeskSession(models.Model):
    cashdesk = models.ForeignKey('Cashdesk', on_delete=models.PROTECT)
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
    items = models.ManyToManyField('Item', through='CashdeskSessionItem', blank=True)

    def __str__(self):
        return '#{2} ({0} on {1})'.format(self.user, self.cashdesk, self.pk)


class CashdeskSessionItem(models.Model):
    session = models.ForeignKey('CashdeskSession', on_delete=models.PROTECT,
                                related_name='cashdesk_session_items')
    item = models.ForeignKey('Item', on_delete=models.PROTECT,
                             related_name='cashdesk_session_items')
    amount_before = models.PositiveIntegerField()
    amount_after = models.PositiveIntegerField(null=True, blank=True)
