from django.db import models


class Preorder(models.Model):
    order_code = models.CharField(max_length=254, db_index=True)
    is_paid = models.BooleanField(default=False)
    warning_text = models.TextField(blank=True)

    def __str__(self):
        return self.order_code


class PreorderPosition(models.Model):
    preorder = models.ForeignKey(Preorder, related_name='positions')
    secret = models.CharField(max_length=254, db_index=True, unique=True)
    product = models.ForeignKey('Product', related_name='preorder_positions')

    def __str__(self):
        return "{}-{}".format(self.preorder.order_code, self.secret[:10])

    @property
    def is_redeemed(self):
        from ..utils.checks import is_redeemed

        return is_redeemed(self)

    @property
    def is_paid(self):
        return self.preorder.is_paid

    @property
    def product_name(self):
        return self.product.name

    @property
    def pack_list(self):
        return self.product.pack_list
