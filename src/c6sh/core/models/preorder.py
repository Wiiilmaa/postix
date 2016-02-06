from django.db import models


class Preorder(models.Model):
    order_code = models.CharField(max_length=254, db_index=True)
    is_paid = models.BooleanField(default=False)
    warning_text = models.TextField()

    def __str__(self):
        return self.order_code


class PreorderPosition(models.Model):
    preorder = models.ForeignKey(Preorder, related_name='positions')
    secret = models.CharField(max_length=254, db_index=True)

    def is_redeemed(self):
        raise NotImplementedError()
