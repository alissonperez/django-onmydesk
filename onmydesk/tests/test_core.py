from unittest import mock
from collections import OrderedDict

from django.test import TestCase

from onmydesk.core import datasets, outputs, reports


class SQLDatasetTestCase(TestCase):

    def test_iterate_must_return_next_row(self):
        mocked_cursor = self._create_mocked_cursor()

        with mock.patch('onmydesk.core.datasets.connection.cursor', return_value=mocked_cursor):
            dataset = datasets.SQLDataset('SELECT * FROM flunfa')

            with dataset:
                results = []
                for item in dataset.iterate():
                    results.append(item)

        expected_result = [
            OrderedDict([('name', 'Alisson'), ('age', 25)]),
            OrderedDict([('name', 'Joao'), ('age', 12)]),
        ]

        self.assertEqual(results, expected_result)

    def test_iterate_must_call_execute_with_query_params(self):
        mocked_cursor = self._create_mocked_cursor()

        with mock.patch('onmydesk.core.datasets.connection.cursor', return_value=mocked_cursor):
            dataset = datasets.SQLDataset('SELECT * FROM flunfa WHERE id = %s', [1])
            with dataset:
                for i in dataset.iterate():
                    pass

        mocked_cursor.execute.assert_called_once_with('SELECT * FROM flunfa WHERE id = %s', [1])

    def test_iterate_must_call_correct_db_alias(self):
        db_alias = 'my-db-alias'
        my_connection = mock.MagicMock()
        my_connection.cursor.return_value = self._create_mocked_cursor()

        connections = {db_alias: my_connection}

        with mock.patch('onmydesk.core.datasets.connection', connections):
            dataset = datasets.SQLDataset('SELECT * FROM flunfa WHERE id = %s', [1], db_alias=db_alias)
            with dataset:
                for i in dataset.iterate():
                    pass

        self.assertTrue(my_connection.cursor.called)

    def _create_mocked_cursor(self):
        mocked_cursor = mock.MagicMock()

        mocked_cursor.description = [
            ('name', 'Other info...'),
            ('age', 'Other info...'),
        ]

        mocked_cursor.fetchone.side_effect = [
            ('Alisson', 25),
            ('Joao', 12),
        ]

        return mocked_cursor


class TSVOutputTestCase(TestCase):

    def setUp(self):
        self.gettempdirmocked = self.patch(
            'onmydesk.core.outputs.tempfile.gettempdir', return_value='/tmp')

        uuid4_mocked = mock.MagicMock()
        uuid4_mocked.hex = 'asjkdlajksdlakjdlakjsdljalksdjla'
        self.uuid4_mocked = self.patch(
            'onmydesk.core.outputs.uuid4', return_value=uuid4_mocked)

        self.open_mocked = mock.mock_open()
        self.patch('builtins.open', self.open_mocked)

        self.test_dataset = mock.MagicMock()
        self.test_dataset.iterate.return_value = [
            ('Alisson', 38),
            ('Joao', 13),
        ]

    def patch(self, *args, **kwargs):
        patcher = mock.patch(*args, **kwargs)
        thing = patcher.start()
        self.addCleanup(patcher.stop)
        return thing

    def test_filepath_must_be_a_tsv_file(self):
        output = outputs.TSVOutput()
        output.process(self.test_dataset, header=('Name', 'Age'))

        self.assertEqual(output.filepath, '/tmp/asjkdlajksdlakjdlakjsdljalksdjla.tsv')

    def test_process_must_write_data_into_a_file(self):
        output = outputs.TSVOutput()
        output.process(self.test_dataset, header=('Name', 'Age'), footer=('test footer',))

        expected_calls = [
            mock.call('/tmp/asjkdlajksdlakjdlakjsdljalksdjla.tsv', 'w+'),
            mock.call().__enter__(),
            mock.call().write('Name\tAge\n'),
            mock.call().write('Alisson\t38\n'),
            mock.call().write('Joao\t13\n'),
            mock.call().write('test footer\n'),
            mock.call().__exit__(None, None, None)
        ]

        self.assertEqual(self.open_mocked.mock_calls, expected_calls)

    def test_process_with_dataset_with_ordered_dict_must_write_data_into_a_file(self):
        self.test_dataset.iterate.return_value = [
            OrderedDict([('name', 'Alisson'), ('age', 38)]),
            OrderedDict([('name', 'Joao'), ('age', 13)]),
        ]

        output = outputs.TSVOutput()
        output.process(self.test_dataset, header=('Name', 'Age'), footer=('test footer',))

        expected_calls = [
            mock.call('/tmp/asjkdlajksdlakjdlakjsdljalksdjla.tsv', 'w+'),
            mock.call().__enter__(),
            mock.call().write('Name\tAge\n'),
            mock.call().write('Alisson\t38\n'),
            mock.call().write('Joao\t13\n'),
            mock.call().write('test footer\n'),
            mock.call().__exit__(None, None, None)
        ]

        self.assertEqual(self.open_mocked.mock_calls, expected_calls)

    def test_row_cleaner_must_change_row_content(self):
        def row_cleaner(row):
            return ('Test', 99)

        output = outputs.TSVOutput()
        output.row_cleaner = row_cleaner
        output.process(self.test_dataset, header=('Name', 'Age'), footer=('test footer',))

        expected_calls = [
            mock.call('/tmp/asjkdlajksdlakjdlakjsdljalksdjla.tsv', 'w+'),
            mock.call().__enter__(),
            mock.call().write('Name\tAge\n'),
            mock.call().write('Test\t99\n'),
            mock.call().write('Test\t99\n'),
            mock.call().write('test footer\n'),
            mock.call().__exit__(None, None, None)
        ]

        self.assertEqual(self.open_mocked.mock_calls, expected_calls)


class CSVOutputTestCase(TestCase):

    def setUp(self):
        self.gettempdirmocked = self.patch(
            'onmydesk.core.outputs.tempfile.gettempdir', return_value='/tmp')

        self.test_dataset = mock.MagicMock()
        self.test_dataset.iterate.return_value = [
            ('Alisson', 38),
            ('Joao', 13),
        ]

        self.open_mocked = mock.mock_open()
        self.patch('builtins.open', self.open_mocked)

        self.writer_mocked = mock.MagicMock()
        self.patch('onmydesk.core.outputs.csv.writer',
                   return_value=self.writer_mocked)

        uuid4_mocked = mock.MagicMock()
        uuid4_mocked.hex = 'asjkdlajksdlakjdlakjsdljalksdjla'
        self.uuid4_mocked = self.patch(
            'onmydesk.core.outputs.uuid4', return_value=uuid4_mocked)

    def patch(self, *args, **kwargs):
        patcher = mock.patch(*args, **kwargs)
        thing = patcher.start()
        self.addCleanup(patcher.stop)
        return thing

    def test_filepath_must_be_a_csv_file(self):
        output = outputs.CSVOutput()
        output.process(self.test_dataset)

        expected_filepath = '/tmp/asjkdlajksdlakjdlakjsdljalksdjla.csv'

        self.assertEqual(output.filepath, expected_filepath)

    def test_process_must_write_data_into_a_file(self):
        output = outputs.CSVOutput()
        output.process(self.test_dataset, header=('Name', 'Age'), footer=('test footer',))

        expected_calls = [
            mock.call(['Name', 'Age']),
            mock.call(['Alisson', '38']),
            mock.call(['Joao', '13']),
            mock.call(['test footer']),
        ]

        self.assertEqual(self.writer_mocked.writerow.mock_calls, expected_calls)

    def test_process_with_ordered_dict_dataset_must_write_into_a_file(self):
        self.test_dataset.iterate.return_value = [
            OrderedDict([('name', 'Alisson'), ('age', 38)]),
            OrderedDict([('name', 'Joao'), ('age', 13)]),
        ]

        output = outputs.CSVOutput()
        output.process(self.test_dataset, header=('Name', 'Age'), footer=('test footer',))

        expected_calls = [
            mock.call(['Name', 'Age']),
            mock.call(['Alisson', '38']),
            mock.call(['Joao', '13']),
            mock.call(['test footer']),
        ]

        self.assertEqual(self.writer_mocked.writerow.mock_calls, expected_calls)

    def test_row_cleaner_must_change_row_content(self):
        def row_cleaner(row):
            return ('Test', 99)

        output = outputs.CSVOutput()
        output.row_cleaner = row_cleaner
        output.process(self.test_dataset, header=('Name', 'Age'), footer=('test footer',))

        expected_calls = [
            mock.call(['Name', 'Age']),
            mock.call(['Test', '99']),
            mock.call(['Test', '99']),
            mock.call(['test footer']),
        ]

        self.assertEqual(self.writer_mocked.writerow.mock_calls, expected_calls)


class SQLReportTestCase(TestCase):

    def setUp(self):
        self.sqldataset_mocked = mock.MagicMock()
        self.patch('onmydesk.core.reports.datasets.SQLDataset',
                   return_value=self.sqldataset_mocked)

        self.tsvoutput_mocked = self.patch('onmydesk.core.reports.outputs.TSVOutput')
        self.tsvoutput_mocked.filepath = '/tmp/asjkdlajksdlakjdlakjsdljalksdjla.tsv'

    def patch(self, *args, **kwargs):
        patcher = mock.patch(*args, **kwargs)
        thing = patcher.start()
        self.addCleanup(patcher.stop)
        return thing

    def test_process_will_call_output_with_dataset(self):
        report = self._create_report()

        report.process()

        with self.sqldataset_mocked as ds:
            self.tsvoutput_mocked.process.assert_called_once_with(
                ds, header=report.header, footer=report.footer)

    def test_process_must_fill_output_filepaths(self):
        report = self._create_report()
        report.process()

        self.assertEqual(report.output_filepaths, [self.tsvoutput_mocked.filepath])

    def test_process_must_fill_row_cleaner_function_to_output_instance(self):
        report = self._create_report()
        report.process()

        self.assertEqual(self.tsvoutput_mocked.row_cleaner, report.row_cleaner)

    def _create_report(self):
        report = reports.SQLReport()
        report.outputs = (self.tsvoutput_mocked,)
        report.query = 'SELECT * FROM test_table'
        report.header = ('Name', 'Age')
        report.footer = ('Footer',)

        return report
