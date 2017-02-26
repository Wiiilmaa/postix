import os
import shutil

from django.core.management.base import BaseCommand
from django.utils.timezone import now

from postix.core.models import CashdeskSession


class Command(BaseCommand):
    help = 'Creates a directory called `export-yyyy-mm-dd-hhmmss` and collects copies of every session\'s most recent report.'

    def handle(self, *args, **kwargs):
        export_dir = os.path.join('.', 'export-{}'.format(now().strftime('%Y-%m-%d-%H%M%S')))
        os.mkdir(export_dir)
        successful_exports = 0
        failed_exports = []

        for session in CashdeskSession.objects.filter(end__isnull=False):
            report_path = session.get_report_path()
            if report_path:
                shutil.copy2(report_path, export_dir)
                successful_exports += 1
            else:
                failed_exports.append(session.pk)

        success_msg = 'Exported {} reports to directory {}.'.format(successful_exports, export_dir)
        self.stdout.write(self.style.SUCCESS(success_msg))

        if failed_exports:
            warn_msg = 'Could not find reports for {} finished sessions (IDs: {}).'.format(
                len(failed_exports),
                failed_exports,
            )
            self.stdout.write(self.style.WARNING(warn_msg))
