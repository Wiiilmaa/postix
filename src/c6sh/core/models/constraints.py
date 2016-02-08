from decimal import Decimal

from django.db import models


class AbstractConstraint(models.Model):
    name = models.CharField(max_length=254)

    class Meta:
        abstract = True


class Quota(AbstractConstraint):
    size = models.PositiveIntegerField()
    products = models.ManyToManyField('Product', verbose_name='Affected products',
                                      blank=True)

    def is_available(self):
        total = sum([product.amount_sold() for product in self.products])
        return total < self.size

    def __str__(self):
        return "{} ({})".format(self.name, self.size)


class TimeConstraint(AbstractConstraint):
    start = models.DateTimeField(null=True, blank=True,
                                 verbose_name='Not available before')
    end = models.DateTimeField(null=True, blank=True,
                               verbose_name='Not available after')
    products = models.ManyToManyField('Product', verbose_name='Affected products',
                                      blank=True)

    def __str__(self):
        return "{} ({} - {})".format(self.name, self.start, self.end)


class ListConstraintProduct(models.Model):
    product = models.OneToOneField('Product', on_delete=models.PROTECT,
                                   related_name='product_list_constraint')
    constraint = models.ForeignKey('ListConstraint', on_delete=models.PROTECT,
                                   related_name='product_constraints')
    price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    tax_rate = models.DecimalField(max_digits=5, decimal_places=2, default=Decimal("0.00"))


class ListConstraint(AbstractConstraint):
    products = models.ManyToManyField('Product', verbose_name='Affected products',
                                      blank=True, through='ListConstraintProduct')

    def __str__(self):
        return self.name


class ListConstraintEntry(models.Model):
    list = models.ForeignKey('ListConstraint', related_name='entries',
                             on_delete=models.PROTECT)
    name = models.CharField(max_length=254)
    identifier = models.CharField(max_length=254)

    def __str__(self):
        return "{} ({}) – {}".format(self.name, self.identifier, self.list)


class WarningConstraintProduct(models.Model):
    product = models.ForeignKey('Product', on_delete=models.PROTECT,
                                related_name='product_warning_constraints')
    constraint = models.ForeignKey('WarningConstraint', on_delete=models.PROTECT,
                                   related_name='product_constraints')
    price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    tax_rate = models.DecimalField(max_digits=5, decimal_places=2, default=Decimal("0.00"))


class WarningConstraint(AbstractConstraint):
    products = models.ManyToManyField('Product', verbose_name='Affected products',
                                      blank=True, through='WarningConstraintProduct')
    message = models.TextField()
