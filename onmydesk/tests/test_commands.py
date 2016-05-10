from datetime import date
from django.test import TestCase
from io import StringIO
from unittest import mock

from django.core import management

from onmydesk.models import Report, Scheduler


class SchedulerProcesssTestCase(TestCase):

    def setUp(self):
        # Cleaning up reports
        Report.objects.all().delete()

        def my_output_file_handler(filepath):
            return filepath

        self._patch('onmydesk.models.output_file_handler', my_output_file_handler)

        self._mock_report_import_function()

    def _mock_report_import_function(self):
        self.report_class = mock.MagicMock()
        self.report_class.name = 'My Report'

        self._patch('onmydesk.models.my_import', return_value=self.report_class)

    def _patch(self, *args, **kwargs):
        patcher = mock.patch(*args, **kwargs)
        thing = patcher.start()
        self.addCleanup(patcher.stop)
        return thing

    def test_call_must_not_out_errors(self):
        scheduler = Scheduler(report='my_report_class',
                              periodicity=Scheduler.PER_MON_SUN)
        scheduler.save()

        errout = StringIO()
        management.call_command('scheduler_process', stderr=errout)

        self.assertEqual(len(errout.getvalue()), 0, errout.getvalue())

    def test_call_must_call_process_from_scheduler(self):
        with mock.patch('onmydesk.models.Scheduler.process') as process_mocked:
            scheduler = Scheduler(report='my_report_class',
                                  periodicity=Scheduler.PER_MON_SUN)
            scheduler.save()

            management.call_command('scheduler_process')

            self.assertTrue(process_mocked.called)

    def test_call_must_have_first_and_last_message_correct(self):
        scheduler = Scheduler(report='my_report_class',
                              periodicity=Scheduler.PER_MON_SUN)
        scheduler.save()

        out = StringIO()
        management.call_command('scheduler_process', stdout=out)

        first_line, *_, last_line, blank_line = out.getvalue().split('\n')

        first_message = 'Starting scheduler process'
        last_message = 'Scheduler #{} processed'.format(scheduler.id)

        self.assertEqual(first_line, first_message)
        self.assertEqual(last_line, last_message)

    def test_call_must_create_correct_report(self):
        scheduler = Scheduler(report='my_report_class',
                              periodicity=Scheduler.PER_MON_SUN)
        scheduler.save()

        self.assertEqual(Report.objects.all().count(), 0)

        out = StringIO()
        management.call_command('scheduler_process', stdout=out)

        self.assertEqual(Report.objects.all().count(), 1)

        repo = Report.objects.all().first()
        self.assertEqual(repo.report, 'my_report_class')

    def test_call_must_not_process_schedulers_from_other_day(self):
        # Forcing a date on sunday
        sunday_date = date(2016, 5, 15)
        date_mocked = mock.MagicMock()
        date_mocked.today.return_value = sunday_date
        with mock.patch('onmydesk.management.commands.scheduler_process.date',
                        return_value=date_mocked):
            # Creating a report scheduled to monday
            scheduler = Scheduler(report='my_report_class',
                                  periodicity=Scheduler.PER_MON)
            scheduler.save()

            self.assertEqual(Report.objects.all().count(), 0)
            management.call_command('scheduler_process')
            self.assertEqual(Report.objects.all().count(), 0)
