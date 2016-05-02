from django.core.management.base import BaseCommand
from onmydesk.models import Report


class Command(BaseCommand):
    help = 'Process pending reports'

    def handle(self, *args, **options):
        items = Report.objects.filter(status=Report.STATUS_PENDING)

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
