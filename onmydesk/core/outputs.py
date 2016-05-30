import tempfile
import csv
import xlsxwriter
from slugify import slugify
from datetime import date

from hashlib import sha224
from uuid import uuid4
from abc import ABCMeta, abstractmethod


class BaseOutput(metaclass=ABCMeta):
    """An abstract representation of an Output class.

    We need to use instances of this classes with context manager. E.g.::

        from onmydesk.core.outputs import XLSXOutput

        myout = XLSXOutput()

        with myout as output:
            output.header(['Name', 'Age'])
            output.out(['Alisson', 39])
            output.out(['Joao', 16])
            output.footer(['Total', 55])
            print(output.filepath)
    """

    filepath = None
    """Filepath with output result which is filled by :func:`process`."""

    file_extension = None
    """File extension to be used on file name output. E.g.: 'csv'"""

    name = None
    """Name used to compose output filename"""

    def __init__(self):
        self.filepath = None

    def header(self, content):
        """Output a header content
        :param mixed content: Content to be written"""

        self.out(content)

    @abstractmethod
    def out(self, content):
        """Output a normal content
        :param mixed content: Content to be written"""

        raise NotImplemented()

    def footer(self, content):
        """Output a footer content
        :param mixed content: Content to be written"""
        self.out(content)

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        pass

    def gen_tmpfilename(self):
        """Utility to be used to generate a temporary filename.

        :returns: Temporary filepath.
        :rtype: str"""

        name = ''
        if self.name:
            name = '{}-'.format(
                slugify(self.name, to_lower=True)[:30].strip('-'))

        filename = '{}{}-{}.{}'.format(
            name,
            date.today().strftime('%Y-%m-%d'),
            sha224(uuid4().hex.encode()).hexdigest()[:7],
            self.file_extension)

        return '{}/{}'.format(
            tempfile.gettempdir(), filename)


class SVOutput(BaseOutput, metaclass=ABCMeta):
    '''Abstract separated values output'''

    delimiter = None

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.writer = None
        self.filepath = None

    def out(self, content):
        if isinstance(content, dict):
            self.writer.writerow([str(i) for i in content.values()])
        else:
            self.writer.writerow([str(i) for i in content])

    def __enter__(self):
        self.filepath = self.gen_tmpfilename()
        self.tmpfile = open(self.filepath, 'w+')
        self.writer = csv.writer(self.tmpfile, delimiter=self.delimiter)
        return self

    def __exit__(self, *args, **kwargs):
        super().__exit__(*args, **kwargs)
        self.tmpfile.close()


class CSVOutput(SVOutput):
    """An output to generate CSV files (files with cols separated by comma)."""

    delimiter = ','
    file_extension = 'csv'


class TSVOutput(SVOutput):
    """An output to generate TSV files (files with cols separated by tabs)."""

    delimiter = '\t'
    file_extension = 'tsv'


class XLSXOutput(BaseOutput):
    """Output to generate XLSX files."""

    file_extension = 'xlsx'

    min_width = 8.43
    """Min width used to set column widths"""

    def header(self, content):
        """Output a header content
        :param mixed content: Content to be written"""

        self.has_header = True
        self._write_row(content, self.header_format)

    def out(self, content):
        """Output a normal content
        :param mixed content: Content to be written"""

        self._write_row(content)

    def footer(self, content):
        """Output a footer content
        :param mixed content: Content to be written"""

        self._write_row(content, self.footer_format)

    def _write_row(self, content, line_format=None):
        values = content
        if isinstance(content, dict):
            values = [a for a in content.values()]

        self._compute_line_widths(values)

        if line_format:
            self.worksheet.write_row(self.current_row, 0, values, line_format)
        else:
            self.worksheet.write_row(self.current_row, 0, values)

        self.current_row += 1

    def _compute_line_widths(self, line):
        for i, v in enumerate(line):
            self.line_widths[i] = max(len(str(v)),
                                      self.line_widths.get(i, self.min_width))

    def __enter__(self):
        self.filepath = self.gen_tmpfilename()
        self.workbook = xlsxwriter.Workbook(self.filepath)
        self.worksheet = self.workbook.add_worksheet()

        self.header_format = self.workbook.add_format({'bold': True, 'bg_color': '#C9C9C9'})
        self.footer_format = self.workbook.add_format({'bold': True, 'bg_color': '#DDDDDD'})

        self.current_row = 0

        self.line_widths = {}

        self.has_header = False

        return self

    def __exit__(self, *args, **kwargs):
        # Freeze first row if report has header
        if self.has_header:
            self.worksheet.freeze_panes(1, 0)

        for i, v in self.line_widths.items():
            self.worksheet.set_column(i, i, v)

        self.workbook.close()
