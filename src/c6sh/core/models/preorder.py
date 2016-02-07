from django.db import models


class Preorder(models.Model):
    order_code = models.CharField(max_length=254, db_index=True)
    is_paid = models.BooleanField(default=False)
    warning_text = models.TextField()

    def __str__(self):
        return self.order_code


class PreorderPosition(models.Model):
    preorder = models.ForeignKey(Preorder, related_name='positions')
    secret = models.CharField(max_length=254, db_index=True, unique=True)
    product = models.ForeignKey('Product', related_name='preorder_positions')

    def __str__(self):
        return "{}-{}".format(self.preorder.order_code, self.secret[:10])

    def is_redeemed(self):
        raise NotImplementedError()
