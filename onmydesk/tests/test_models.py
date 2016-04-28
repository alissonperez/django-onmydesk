from unittest import mock
from django.test import TestCase


from onmydesk.models import Report, output_file_handler, ReportNotSavedException


class OutputFileHandlerTestCase(TestCase):

    def test_call_must_return_filepath_changed(self):
        my_handler = 'path.to.my.handler'
        with mock.patch('onmydesk.models.ONMYDESK_FILE_HANDLER', my_handler):
            my_handler_mocked = mock.MagicMock(return_value='/tmp/filepath-changed.tsv')
            with mock.patch('onmydesk.models.my_import', return_value=my_handler_mocked) as my_import_mocked:
                self.assertEqual(
                    output_file_handler('/tmp/filepath.tsv'),
                    '/tmp/filepath-changed.tsv')

        my_import_mocked.assert_called_once_with(my_handler)
        my_handler_mocked.assert_called_once_with('/tmp/filepath.tsv')

    def test_call_must_return_same_filepath_if_a_file_handler_not_exists(self):
        with mock.patch('onmydesk.models.ONMYDESK_FILE_HANDLER', None):
            self.assertEqual(output_file_handler('/tmp/filepath.tsv'), '/tmp/filepath.tsv')


class ReportTestCase(TestCase):

    def setUp(self):
        def my_output_file_handler(filepath):
            return filepath

        self.patch('onmydesk.models.output_file_handler', my_output_file_handler)

        self.report_instance = mock.MagicMock()
        self.report_instance.output_filepaths = ['/tmp/flunfa.tsv']
        self.report_class = mock.MagicMock(return_value=self.report_instance)
        self.my_import_mocked = self.patch('onmydesk.models.my_import', return_value=self.report_class)

    def test_process_must_call_process_from_report_class(self):
        report = Report(report='my_report_class')
        report.save()
        report.process()

        self.my_import_mocked.assert_called_once_with(report.report)
        self.assertTrue(self.report_instance.process.called)

    def test_process_with_not_saved_report_must_raise_a_exception(self):
        report = Report(report='my_report_class')
        self.assertRaises(ReportNotSavedException, report.process)

    def test_process_must_store_filepaths_result(self):
        self.report_instance.output_filepaths = [
            '/tmp/flunfa-2.tsv',
            '/tmp/flunfa-3.tsv',
        ]

        report = Report(report='my_report_class')
        report.save()
        report.process()

        self.assertEqual(
            report.results, ';'.join(self.report_instance.output_filepaths))

    def test_process_with_params_must_call_report_constructor_with_these_params(self):
        report = Report(report='my_report_class')
        report.save()
        params = {'type': 'whatever'}
        report.process(report_params=params)

        self.report_class.assert_called_once_with(params=params)

    def test_process_must_set_status_as_processing_when_start(self):
        self.patch('onmydesk.models.my_import', side_effect=Exception)

        report = Report(report='my_report_class')
        report.save()

        self.assertEqual(report.status, Report.STATUS_PENDING)

        try:
            report.process()
        except Exception:
            pass

        report.refresh_from_db()
        self.assertEqual(report.status, Report.STATUS_PROCESSING)

    def test_process_must_set_status_as_processed_after_report_process(self):
        report = Report(report='my_report_class')
        report.save()
        report.process()

        report.refresh_from_db()
        self.assertEqual(report.status, Report.STATUS_PROCESSED)

    def test_process_must_set_status_as_error_if_some_exception_is_raised(self):
        self.report_instance.process.side_effect = Exception()

        report = Report(report='my_report_class')
        report.save()
        report.process()

        self.assertEqual(report.status, Report.STATUS_ERROR)
    def test_results_as_list_must_return_a_list(self):
        expected_results = [
            '/tmp/flunfa-2.tsv',
            '/tmp/flunfa-3.tsv',
        ]

        report = Report(report='my_report_class')
        report.results = ';'.join(expected_results)

        self.assertEqual(report.results_as_list, expected_results)

    def test_results_as_list_must_return_empty_list_if_field_is_empty(self):
        report = Report(report='my_report_class')
        report.results = ''

        self.assertEqual(report.results_as_list, [])

    def patch(self, *args, **kwargs):
        patcher = mock.patch(*args, **kwargs)
        thing = patcher.start()
        self.addCleanup(patcher.stop)
        return thing
