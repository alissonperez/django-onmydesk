import tempfile
from os import path

from django.core.management.base import BaseCommand

import filelock
from onmydesk.models import Report


class Command(BaseCommand):
    help = 'Process pending reports'

    def handle(self, *args, **options):
        try:
            self._process_with_lock()
        except Exception as e:
            self.stdout.write('Error: {}'.format(str(e)))

    def _process_with_lock(self):
        lock = filelock.FileLock(self._get_lock_filepath())

        with lock.acquire(timeout=10):
            self._process_reports()

    def _process_reports(self):
        items = Report.objects.filter(status=Report.STATUS_PENDING)[:10]

        count = len(items)

        self.stdout.write('Found {} reports to process'.format(count))
        for i, report in enumerate(items, start=1):
            self.stdout.write('Processing report #{} - {} of {}'.format(
                report.id, i, count))

            try:
                report.process()
                report.save()
                self.stdout.write('Report #{} processed'.format(report.id))
            except Exception as e:
                self.stderr.write('Error processing report #{}: {}'.format(
                    report.id, str(e)))

    def _get_lock_filepath(self):
        return path.join(tempfile.gettempdir(), 'onmydesk-report-processor-lock')
