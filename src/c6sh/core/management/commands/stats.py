from django.core.management.base import BaseCommand
from django.db.models import Count

from c6sh.core.models import TransactionPosition


class Command(BaseCommand):
    help = 'Print a view stats'

    def handle(self, *args, **kwargs):
        agg = TransactionPosition.objects.order_by('product').values("product__name", "product__price").annotate(c=Count('id'), r=Count('reverses'))
        total = 0
        for line in agg:
            s = line['c'] - line['r']
            print("{l[product__name]:30} {l[product__price]:>20} EUR       {s}".format(l=line, s=s))
            if 'ticket' in line['product__name']:
                total += s

        print("Total tickets: {total}".format(total=total))
