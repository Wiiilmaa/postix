from django.db import models


class AbstractConstraint(models.Model):
    name = models.CharField(max_length=254)
    products = models.ManyToManyField('Product', verbose_name='Affected products',
                                      blank=True)

    class Meta:
        abstract = True


class Quota(AbstractConstraint):
    size = models.PositiveIntegerField()

    def __str__(self):
        return "{} ({})".format(self.name, self.size)


class TimeConstraint(AbstractConstraint):
    start = models.DateTimeField(null=True, blank=True,
                                 verbose_name='Not available before')
    end = models.DateTimeField(null=True, blank=True,
                               verbose_name='Not available after')

    def __str__(self):
        return "{} ({} - {})".format(self.name, self.start, self.end)


class ListConstraint(AbstractConstraint):

    def __str__(self):
        return self.name


class ListConstraintEntry(models.Model):
    list = models.ForeignKey('ListConstraint', related_name='entries',
                             on_delete=models.PROTECT)
    name = models.CharField(max_length=254)
    identifier = models.CharField(max_length=254)

    def __str__(self):
        return "{} ({}) – {}".format(self.name, self.identifier, self.list)
