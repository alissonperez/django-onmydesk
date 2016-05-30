from datetime import date
from unittest import mock
from hashlib import sha224
from collections import OrderedDict
from slugify import slugify

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

    def test_iterate_with_no_context_manager_must_return_result(self):
        mocked_cursor = self._create_mocked_cursor()

        with mock.patch('onmydesk.core.datasets.connection.cursor', return_value=mocked_cursor):
            dataset = datasets.SQLDataset('SELECT * FROM flunfa')
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

        with mock.patch('onmydesk.core.datasets.connections', connections):
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


class BaseOutputTestCase(TestCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        def out(self, content):
            pass

        cls.output_class = type('MyOutput', (outputs.BaseOutput,),
                                {'out': out,
                                 'file_extension': 'txt'})

    def setUp(self):
        self.uuid4_obj = mock.MagicMock()
        self.uuid4_obj.hex = 'kjaljjp1ojq2q3jlqjljql23jlqj3ql2'

        self._patch('onmydesk.core.outputs.tempfile.gettempdir', return_value='/tmp')

    def _patch(self, *args, **kwargs):
        patcher = mock.patch(*args, **kwargs)
        thing = patcher.start()
        self.addCleanup(patcher.stop)
        return thing

    def test_gen_tmpfilename_must_return_string(self):
        obj = self.output_class()
        self.assertIsInstance(obj.gen_tmpfilename(), str)

    def test_gen_tmpfilename_must_add_current_date(self):
        obj = self.output_class()

        date_str = date.today().strftime('%Y-%m-%d')
        hash_used = sha224(self.uuid4_obj.hex.encode()).hexdigest()[:7]
        expected_filename = '{}/{}-{}.{}'.format(
            '/tmp',
            date_str,
            hash_used,
            'txt')

        with mock.patch('onmydesk.core.outputs.uuid4', return_value=self.uuid4_obj):
            self.assertEqual(expected_filename, obj.gen_tmpfilename())

    def test_gen_tmpfilename_must_include_name_slugfied_if_param_filled(self):
        obj = self.output_class()
        obj.name = 'My report about Something'

        date_str = date.today().strftime('%Y-%m-%d')
        hash_used = sha224(self.uuid4_obj.hex.encode()).hexdigest()[:7]
        expected_filename = '{}/{}-{}-{}.{}'.format(
            '/tmp',
            slugify(obj.name, to_lower=True),
            date_str,
            hash_used,
            'txt')

        with mock.patch('onmydesk.core.outputs.uuid4', return_value=self.uuid4_obj):
            self.assertEqual(expected_filename, obj.gen_tmpfilename())

    def test_gen_tmpfilename_must_include_name_slugfied_with_len_limit(self):
        obj = self.output_class()
        obj.name = 'My report about Something with a long report name'

        date_str = date.today().strftime('%Y-%m-%d')
        hash_used = sha224(self.uuid4_obj.hex.encode()).hexdigest()[:7]
        expected_filename = '{}/{}-{}-{}.{}'.format(
            '/tmp',
            slugify(obj.name, to_lower=True)[:30].strip('-'),
            date_str,
            hash_used,
            'txt')

        with mock.patch('onmydesk.core.outputs.uuid4', return_value=self.uuid4_obj):
            self.assertEqual(expected_filename, obj.gen_tmpfilename())


class TSVOutputTestCase(TestCase):

    def setUp(self):
        self.gettempdirmocked = self.patch(
            'onmydesk.core.outputs.tempfile.gettempdir', return_value='/tmp')

        uuid4_mocked = mock.MagicMock()
        uuid4_mocked.hex = 'asjkdlajksdlakjdlakjsdljalksdjla'
        self.uuid4_mocked = self.patch(
            'onmydesk.core.outputs.uuid4', return_value=uuid4_mocked)

        self.open_result_mocked = mock.MagicMock()
        self.open_mocked = mock.mock_open()
        self.open_mocked.return_value = self.open_result_mocked
        self.patch('builtins.open', self.open_mocked)

        self.writer = mock.MagicMock()
        self.patch('onmydesk.core.outputs.csv.writer', return_value=self.writer)

        self.iterable_object = [
            ('Alisson', 38),
            ('Joao', 13),
        ]

    def patch(self, *args, **kwargs):
        patcher = mock.patch(*args, **kwargs)
        thing = patcher.start()
        self.addCleanup(patcher.stop)
        return thing

    def test_filepath_must_be_a_tsv_file(self):
        with outputs.TSVOutput() as output:
            output.out(('Alisson', 38))

            *_, extension = output.filepath.split('.')

            self.assertEqual(extension, 'tsv')

    def test_out_must_call_open_with_correct_parameters(self):
        with outputs.TSVOutput() as output:
            output.out(('Alisson', 38))
            filename = output.filepath

        self.open_mocked.assert_called_once_with(filename, 'w+')

    def test_context_manager_must_close_file(self):
        with outputs.TSVOutput() as output:
            output.out(('Alisson', 38))

            self.assertFalse(self.open_result_mocked.close.called)

        self.assertTrue(self.open_result_mocked.close.called)

    def test_out_must_write_correct_data_in_csv_writer(self):
        with outputs.TSVOutput() as output:
            output.header(('Name', 'Age'))
            for item in self.iterable_object:
                output.out(item)

            output.footer(('test footer',))

        expected_calls = [
            mock.call(['Name', 'Age']),
            mock.call(['Alisson', '38']),
            mock.call(['Joao', '13']),
            mock.call(['test footer']),
        ]

        self.assertEqual(self.writer.writerow.mock_calls, expected_calls)

    def test_process_with_dataset_with_ordered_dict_must_write_data_into_a_file(self):
        iterable_object = [
            OrderedDict([('name', 'Alisson'), ('age', 38)]),
            OrderedDict([('name', 'Joao'), ('age', 13)]),
        ]

        with outputs.TSVOutput() as output:
            output.header(('Name', 'Age'))
            for item in iterable_object:
                output.out(item)

            output.footer(('test footer',))

        expected_calls = [
            mock.call(['Name', 'Age']),
            mock.call(['Alisson', '38']),
            mock.call(['Joao', '13']),
            mock.call(['test footer']),
        ]

        self.assertEqual(self.writer.writerow.mock_calls, expected_calls)


class CSVOutputTestCase(TestCase):

    def setUp(self):
        self.gettempdirmocked = self.patch(
            'onmydesk.core.outputs.tempfile.gettempdir', return_value='/tmp')

        self.iterable_object = [
            ('Alisson', 38),
            ('Joao', 13),
        ]

        self.open_result_mocked = mock.MagicMock()
        self.open_mocked = mock.mock_open()
        self.open_mocked.return_value = self.open_result_mocked
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
        with outputs.CSVOutput() as output:
            output.out(('Alisson', 38))

            *_, extension = output.filepath.split('.')

            self.assertEqual(extension, 'csv')

    def test_context_manager_must_close_file(self):
        with outputs.CSVOutput() as output:
            output.out(('Alisson', 38))

            self.assertFalse(self.open_result_mocked.close.called)

        self.assertTrue(self.open_result_mocked.close.called)

    def test_process_must_write_data_into_a_file(self):
        with outputs.CSVOutput() as output:
            output.header(('Name', 'Age'))
            for item in self.iterable_object:
                output.out(item)

            output.footer(('test footer',))

        expected_calls = [
            mock.call(['Name', 'Age']),
            mock.call(['Alisson', '38']),
            mock.call(['Joao', '13']),
            mock.call(['test footer']),
        ]

        self.assertEqual(self.writer_mocked.writerow.mock_calls, expected_calls)

    def test_process_with_ordered_dict_dataset_must_write_into_a_file(self):
        iterable_object = [
            OrderedDict([('name', 'Alisson'), ('age', 38)]),
            OrderedDict([('name', 'Joao'), ('age', 13)]),
        ]

        with outputs.CSVOutput() as output:
            output.header(('Name', 'Age'))
            for item in iterable_object:
                output.out(item)

            output.footer(('test footer',))

        expected_calls = [
            mock.call(['Name', 'Age']),
            mock.call(['Alisson', '38']),
            mock.call(['Joao', '13']),
            mock.call(['test footer']),
        ]

        self.assertEqual(self.writer_mocked.writerow.mock_calls, expected_calls)


class XLSXOutputTestCase(TestCase):

    def setUp(self):
        self.gettempdirmocked = self._patch(
            'onmydesk.core.outputs.tempfile.gettempdir', return_value='/tmp')

        self.worksheet_mocked = mock.MagicMock()
        self.workbook_mocked = mock.MagicMock()
        self.workbook_mocked.add_worksheet.return_value = self.worksheet_mocked
        self.workbook_const_mocked = self._patch('onmydesk.core.outputs.xlsxwriter.Workbook',
                                                 return_value=self.workbook_mocked)

        self.iterable_object = [
            ('Alisson', 38),
            ('Joao', 13),
        ]

        uuid4_mocked = mock.MagicMock()
        uuid4_mocked.hex = 'asjkdlajksdlakjdlakjsdljalksdjla'
        self.uuid4_mocked = self._patch(
            'onmydesk.core.outputs.uuid4', return_value=uuid4_mocked)

    def _patch(self, *args, **kwargs):
        patcher = mock.patch(*args, **kwargs)
        thing = patcher.start()
        self.addCleanup(patcher.stop)
        return thing

    def test_call_out_must_call_lib_constructor(self):
        with outputs.XLSXOutput() as output:
            output.out(('Alisson', 38))

        self.workbook_const_mocked.assert_called_once_with(
            output.filepath)

    def test_call_out_must_call_workbook_add_worksheet(self):
        with outputs.XLSXOutput() as output:
            output.out(('Alisson', 38))

        self.assertTrue(self.workbook_mocked.add_worksheet.called)

    def test_call_out_must_call_add_format_to_header_and_footer(self):
        with outputs.XLSXOutput() as output:
            output.out(('Alisson', 38))

        calls = [
            mock.call({'bold': True, 'bg_color': '#C9C9C9'}),  # header
            mock.call({'bold': True, 'bg_color': '#DDDDDD'}),  # Footer
        ]

        self.assertEqual(self.workbook_mocked.add_format.mock_calls, calls)

    def test_call_out_must_call_write(self):
        with outputs.XLSXOutput() as output:
            output.out(['Alisson', 38])
            output.out(['Joao', 13])

        expected_calls = [
            mock.call(0, 0, ['Alisson', 38]),
            mock.call(1, 0, ['Joao', 13])
        ]

        self.assertEqual(self.worksheet_mocked.write_row.mock_calls, expected_calls)

    def test_call_out_must_call_write_if_we_give_a_dict(self):
        with outputs.XLSXOutput() as output:
            output.out(OrderedDict([('name', 'Alisson'), ('age', 38)]))
            output.out(OrderedDict([('name', 'Joao'), ('age', 13)]))

        expected_calls = [
            mock.call(0, 0, ['Alisson', 38]),
            mock.call(1, 0, ['Joao', 13])
        ]

        self.assertEqual(self.worksheet_mocked.write_row.mock_calls, expected_calls)

    def test_call_process_with_header_and_footer_must_call_write_with_correct_format(self):
        header_format = mock.MagicMock()
        footer_format = mock.MagicMock()

        self.workbook_mocked.add_format.side_effect = [header_format, footer_format]

        with outputs.XLSXOutput() as output:
            output.header(['Name', 'Age'])
            for item in self.iterable_object:
                output.out(item)
            output.footer(['Total', 51])

        first_call, *_, last_call = self.worksheet_mocked.write_row.mock_calls

        # Header
        self.assertEqual(first_call, mock.call(0, 0, ['Name', 'Age'], header_format))

        # Footer (1 of header and the content's length)
        footer_line = 1 + 2
        self.assertEqual(last_call, mock.call(footer_line, 0, ['Total', 51], footer_format))

    def test_call_out_must_freeze_first_line_if_report_received_header(self):
        with outputs.XLSXOutput() as output:
            output.header(['Name', 'Age'])
            for item in self.iterable_object:
                output.out(item)
            output.footer(['Total', 51])

        self.worksheet_mocked.freeze_panes.assert_called_once_with(1, 0)

    def test_call_out_must_not_freeze_first_line_if_report_has_no_header(self):
        with outputs.XLSXOutput() as output:
            for item in self.iterable_object:
                output.out(item)
            output.footer(['Total', 51])

        self.assertFalse(self.worksheet_mocked.freeze_panes.called)

    def test_call_must_set_column_width_with_correct_chars_number(self):
        rows = [
            ('Joao', 'Testing large line', 'Small line'),
            ('Alisson dos Reis Perez', 'Test', 'Width of the column must be max chars number'),
        ]

        with outputs.XLSXOutput() as output:
            for item in rows:
                output.out(item)

        columns_width = {
            0: len(rows[1][0]),
            1: len(rows[0][1]),
            2: len(rows[1][2]),
        }

        calls = [mock.call(i, i, v) for i, v in columns_width.items()]

        self.worksheet_mocked.set_column.assert_has_calls(calls)

    def test_call_out_must_set_column_with_minumum_if_row_value_is_very_small(self):
        rows = [
            ('Jo', 17),
            ('Ali', 45),
        ]

        with outputs.XLSXOutput() as output:
            for item in rows:
                output.out(item)

        columns_width = {
            0: outputs.XLSXOutput().min_width,
            1: outputs.XLSXOutput().min_width,
        }
        calls = [mock.call(i, i, v) for i, v in columns_width.items()]

        self.worksheet_mocked.set_column.assert_has_calls(calls)

    def test_call_out_must_call_close(self):
        with outputs.XLSXOutput() as output:
            for item in self.iterable_object:
                output.out(item)

        self.assertTrue(self.workbook_mocked.close.called)


class BaseReportTestCase(TestCase):

    def setUp(self):
        self._create_dataset()
        self._create_output()

        self.header = ('Name', 'Age')
        self.footer = ('My footer',)

        self.my_report_class = type('my_report_class',
                                    (reports.BaseReport,),
                                    dict(dataset=self.dataset_mocked,
                                         outputs=[self.output_mocked],
                                         header=self.header,
                                         footer=self.footer))

        self.params = dict(age_filter=25)
        self.report = self.my_report_class(params=self.params)

    def _create_dataset(self):
        self.dataset_mocked = mock.MagicMock()
        self.rows = [
            ('Alisson', 38),
            ('Joao', 13),
        ]
        self.dataset_mocked.iterate.return_value = self.rows
        self.dataset_mocked.__enter__.return_value = self.dataset_mocked

    def _create_output(self):
        self.output_mocked = mock.MagicMock()
        self.output_mocked.__enter__.return_value = self.output_mocked

    def _patch(self, *args, **kwargs):
        patcher = mock.patch(*args, **kwargs)
        thing = patcher.start()
        self.addCleanup(patcher.stop)
        return thing

    def test_process_must_call_output_process_with_dataset(self):
        self.report.process()

        self.output_mocked.header.assert_called_once_with(self.header)

        calls = [mock.call(i) for i in self.rows]
        self.assertEqual(self.output_mocked.out.mock_calls, calls)

        self.output_mocked.footer.assert_called_once_with(self.footer)

        self.assertTrue(self.output_mocked.__enter__.called)
        self.assertTrue(self.output_mocked.__exit__.called)

    def test_process_must_call_iterate_from_dataset_with_params(self):
        self.report.process()
        self.dataset_mocked.iterate.assert_called_once_with(params=self.params)

    def test_process_must_not_call_output_header_if_report_has_no_header(self):
        self.report.header = None
        self.report.process()

        self.assertFalse(self.output_mocked.header.called)

    def test_process_must_not_call_output_footer_if_report_has_no_header(self):
        self.report.footer = None
        self.report.process()

        self.assertFalse(self.output_mocked.footer.called)

    def test_process_must_use_row_cleaner_for_each_row_from_dataset(self):
        def my_row_cleaner(self, row):
            return ('Marcondes', 18)

        self.my_report_class.row_cleaner = my_row_cleaner

        self.params = dict(age_filter=25)

        self.report = self.my_report_class(params=self.params)
        self.report.process()

        rows = [('Marcondes', 18)] * len(self.rows)
        calls = [mock.call(i) for i in rows]

        self.assertEqual(self.output_mocked.out.mock_calls, calls)


class SQLReportTestCase(TestCase):

    def setUp(self):
        self.items = [
            (1, 'Test1'),
            (2, 'Test2'),
        ]

        self.sqldataset_mocked = mock.MagicMock()
        self.sqldataset_mocked.iterate.return_value = self.items
        self.sqldataset_mocked.__enter__.return_value = self.sqldataset_mocked
        self.sqldataset_class_mocked = self.patch('onmydesk.core.reports.datasets.SQLDataset',
                                                  return_value=self.sqldataset_mocked)

        self._create_output()

    def _create_output(self):
        self.output_mocked = mock.MagicMock()
        self.output_mocked.filepath = '/tmp/asjkdlajksdlakjdlakjsdljalksdjla.tsv'
        self.output_mocked.__enter__ = mock.MagicMock(
            return_value=self.output_mocked)

    def patch(self, *args, **kwargs):
        patcher = mock.patch(*args, **kwargs)
        thing = patcher.start()
        self.addCleanup(patcher.stop)
        return thing

    def test_process_must_call_output_with_dataset_iterator_result(self):
        report = self._create_report()
        report.process()

        calls = [mock.call(i) for i in self.items]
        self.assertEqual(self.output_mocked.out.mock_calls, calls)

        self.output_mocked.header.assert_called_once_with(report.header)
        self.output_mocked.footer.assert_called_once_with(report.footer)

    def test_process_must_fill_output_filepaths(self):
        report = self._create_report()
        report.process()

        self.assertEqual(report.output_filepaths, [self.output_mocked.filepath])

    def test_dataset_attr_must_return_dataset_with_db_alias_from_report(self):
        report = self._create_report()
        report.db_alias = 'my-db-alias'

        report.dataset

        self.sqldataset_class_mocked.assert_called_once_with(
            report.query, report.query_params, 'my-db-alias')

    def _create_report(self):
        report = reports.SQLReport()
        report.outputs = (self.output_mocked,)
        report.query = 'SELECT * FROM test_table'
        report.header = ('Name', 'Age')
        report.footer = ('Footer',)

        return report
