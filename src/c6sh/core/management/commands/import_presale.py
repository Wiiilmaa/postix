import json
from decimal import Decimal

from django.core.management.base import BaseCommand

from c6sh.core.models import Cashdesk, Preorder, PreorderPosition, Product


class Command(BaseCommand):
    help = 'Imports a pretix-style presale export, generating products and preorder positions.'

    def add_arguments(self, parser):
        parser.add_argument('--add-cashdesks', action='store_true', default=False)
        parser.add_argument('presale_json')

    def handle(self, *args, **kwargs):
        try:
            with open(kwargs['presale_json'], 'r') as user_data:
                presale_export = json.load(user_data)['event']
        except:
            self.stdout.write(self.style.ERROR('Could not open or read file.'))
            return

        self.stdout.write(self.style.NOTICE(
            'Importing data from event "{}".'.format(presale_export['name'])
        ))

        items = presale_export['items']
        orders = presale_export['orders']
        created_items = 0
        loaded_items = 0
        product_dict = dict()

        for item in items:
            if item['variations']:
                self.stdout.write(self.style.ERROR('Warning: Import script cannot deal with variations yet!'))

            # if item['admission'] is True:
            try:
                product = Product.objects.get(import_source_id=item['id'])
                loaded_items += 1
            except Product.DoesNotExist:
                product = Product(import_source_id=item['id'])
                product.price = Decimal(item['price'])
                product.tax_rate = Decimal(item['tax_rate'])
                created_items += 1
            product.name = item['name']
            product.save()
            product_dict[item['id']] = product
            # else:
            #    self.stdout.write(self.style.NOTICE('Non-admission product ignored: {}'.format(item['name'])))

        self.stdout.write(self.style.SUCCESS(
            'Found {} new and {} known products in file.'.format(created_items, loaded_items)
        ))

        created_orders = 0
        loaded_orders = 0
        for order in orders:
            preorder, created = Preorder.objects.get_or_create(
                order_code=order['code']
            )
            preorder.is_paid = (order['status'] == 'p')
            preorder.save()

            if not created:
                preorder_positions = {
                    p.secret: p for p in preorder.positions.all()
                }
            else:
                preorder_positions = {}

            for position in order['positions']:
                if position['secret'] in preorder_positions:
                    pp = preorder_positions[position['secret']]
                    del preorder_positions[position['secret']]
                else:
                    pp = PreorderPosition(preorder=preorder, secret=position['secret'])
                pp.product = product_dict[position['item']]
                pp.save()

            if preorder_positions:
                for pp in preorder_positions.values():
                    pp.delete()

            created_orders += int(created)
            loaded_orders += int(not created)

        self.stdout.write(self.style.SUCCESS(
            'Found {} new and {} known orders in file.'.format(created_orders, loaded_orders)
        ))

        if kwargs.get('add_cashdesks'):
            for cashdesk_number in range(5):
                Cashdesk.objects.get_or_create(
                    name='Cashdesk {}'.format(cashdesk_number + 1),
                    ip_address='127.0.0.{}'.format(cashdesk_number + 1),
                )
            self.stdout.write(self.style.SUCCESS(
                'Added 5 cashdesks.'
            ))
        self.stdout.write(self.style.SUCCESS(
            'Import done.'
        ))
