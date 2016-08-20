import decimal
import json
import os

from django.core.management.base import BaseCommand

from c6sh.core.models import Preorder, PreorderPosition, Product


class Command(BaseCommand):
    help = 'Imports a pretix-style presale export, generating products and preorder positions.'

    def add_arguments(self, parser):
        parser.add_argument('presale_json')

    def handle(self, *args, **kwargs):
        try:
            with open(kwargs['presale_json'], 'r') as user_data:
                presale_export = json.load(user_data)['event']
        except:
            self.stdout.write(self.style.ERROR('Could not open or read file.'))
            return

        items = presale_export['items']
        orders = presale_export['orders']
        created_items = 0
        loaded_items = 0
        product_dict = dict()

        for item in items:
            if item['admission'] == True:
                product, created = Product.objects.get_or_create(
                   name=item['name'], 
                   price=item['price'],
                   tax_rate=decimal.Decimal('19.00'),
                )
                product_dict[item['id']] = product
                created_items += int(created)
                loaded_items += int(not created)

        for order in orders:
            preorder = Preorder.objects.create(
                order_code=order['code'],
                is_paid=(order['status'] == 'p'),
            )
            for position in order['positions']:
                if position['item'] in product_dict:
                    PreorderPosition.objects.create(
                        preorder=preorder,
                        secret=position['secret'],
                        product=product_dict[position['item']],
                    )

        success_msg = 'Imported {} products, loaded {} products and imported {} presale orders.'
        self.stdout.write(self.style.SUCCESS(success_msg.format(created_items, loaded_items, len(orders))))
