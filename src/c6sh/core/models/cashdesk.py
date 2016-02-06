import random
import string

from django.contrib.auth.base_user import AbstractBaseUser
from django.db import models


def generate_key():
    return "".join(random.choice(string.ascii_letters + string.digits) for i in range(32))


class Cashdesk(models.Model):
    name = models.CharField(max_length=254)
    ip_address = models.GenericIPAddressField()
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


class User(AbstractBaseUser):
    username = models.CharField(max_length=254, unique=True)
    firstname = models.CharField(max_length=254)
    lastname = models.CharField(max_length=254)
    is_active = models.BooleanField(default=True)
    is_superuser = models.BooleanField(default=False)
    is_troubleshooter = models.BooleanField(default=False)
    auth_token = models.CharField(max_length=254, null=True, blank=True)

    USERNAME_FIELD = 'username'

    def get_current_session(self):
        return CashdeskSession.objects.filter(user=self, end__isnull=True)\
                                      .order_by('-start').first()

    def has_perm(self, perm, obj=None):
        return self.is_superuser

    def has_module_perms(self, app_label):
        return self.is_superuser

    @property
    def is_staff(self):
        return self.is_superuser or self.is_troubleshooter
