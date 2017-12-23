import csv

from django.core.management.base import BaseCommand
from django.db import transaction

from postix.core.models import ListConstraint, ListConstraintEntry


class Command(BaseCommand):
    help = 'Invocation: import_member ~/member_list.csv [BLN]'

    def add_arguments(self, parser):
        parser.add_argument('member_list')
        parser.add_argument('--prefix')

    def handle(self, *args, **kwargs):
        constraints, _ = ListConstraint.objects.get_or_create(confidential=True, name='Mitglieder')
        import_count= import_known= 0
        local_prefix = kwargs.get('prefix')

        with open(kwargs['member_list'], 'r') as member_list:
            if not local_prefix:
                reader = csv.DictReader(member_list, delimiter='\t')
            else:
                reader = csv.DictReader(member_list, delimiter=';')
            with transaction.atomic():
                for row in reader:
                    if not local_prefix:
                        _, created = ListConstraintEntry.objects.get_or_create(
                            list=constraints,
                            name='{} {}'.format(row['VORNAME'], row['NACHNAME']),
                            identifier=row['CHAOSNR'],
                        )
                    else:
                        _, created = ListConstraintEntry.objects.get_or_create(
                            list=constraints,
                            name=row['NAME'].strip(),
                            identifier='{}-{}'.format(local_prefix, row['CHAOSNR']),
                        )
                    if created:
                        import_count += 1
                    else:
                        import_known+= 1
        self.stdout.write(self.style.SUCCESS('Imported {} entries of the dataset, {} were already known.').format(import_count, import_known))
