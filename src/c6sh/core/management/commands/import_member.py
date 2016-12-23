import csv

from django.core.management.base import BaseCommand

from c6sh.core.models import ListConstraint, ListConstraintEntry


class Command(BaseCommand):
    help = 'Invocation: import_member ~/list_global.csv ~/list_local.csv BLN'

    def add_arguments(self, parser):
        parser.add_argument('list_global')
        parser.add_argument('list_local')
        parser.add_argument('local_prefix')

    def handle(self, *args, **kwargs):
        constraints = ListConstraint.objects.create(confidential=True, name='Mitglieder')
        import_count_global = 0
        import_count_local = 0
        local_prefix = kwargs['local_prefix']

        with open(kwargs['list_global'], 'r') as global_list:
            reader = csv.DictReader(global_list)
            for row in reader:
                ListConstraintEntry.objects.create(
                    list=constraints,
                    name='{} {}'.format(row['VORNAME'], row['NACHNAME']),
                    identifier=row['CHAOSNR'],
                )
                import_count_global += 1

        self.stdout.write(self.style.SUCCESS('Imported {} entries of the global dataset.').format(import_count_global))
        with open(kwargs['list_local'], 'r') as local_list:
            reader = csv.DictReader(local_list)
            for row in reader:
                ListConstraintEntry.objects.create(
                    list=constraints,
                    name=row['NAME'].strip(),
                    identifier='{}-{}'.format(local_prefix, row['CHAOSNR']),
                )
                import_count_local += 1

        self.stdout.write(self.style.SUCCESS('Imported {} entries of the local dataset.').format(import_count_local))
