from django.db import models


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
