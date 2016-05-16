import tempfile
import csv
import xlsxwriter

from uuid import uuid4
from abc import ABCMeta, abstractmethod


class BaseOutput(metaclass=ABCMeta):
    """An abstract representation of an Output class."""

    filepath = None
    """Filepath with output result which is filled by :func:`process`."""

    def __init__(self):
        self.filepath = None

    def header(self, content):
        self.out(content)

    @abstractmethod
    def out(self, content):
        pass

    def footer(self, content):
        self.out(content)

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        pass

    # @abstractmethod
    # def process(self, iterator, header=None, footer=None):
    #     """Process the output given a `iterator`, `header` and `footer`. The result are stored in :attr:`filepath`.

    #     :param iterator iterator: An iterable object.
    #     :param header: Output header.
    #     :param footer: Output footer.
    #     """

    #     raise NotImplemented()

    def gen_tmpfilename(self):
        """Utility to be used to generate a temporary filename.

        :returns: Temporary filepath.
        :rtype: str"""
        return tempfile.gettempdir() + '/' + uuid4().hex


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

    def gen_tmpfilename(self):
        """It generates and returns a CSV temporary file.

        :returns: Temporary CSV file.
        :rtype: str"""

        return super().gen_tmpfilename() + '.csv'


class TSVOutput(SVOutput):
    """An output to generate TSV files (files with cols separated by tabs)."""

    delimiter = '\t'

    def gen_tmpfilename(self):
        """It generates and returns a tsv temporary file.

        :returns: Temporary TSV file.
        :rtype: str"""

        return super().gen_tmpfilename() + '.tsv'


class XLSXOutput(BaseOutput):
    """Output to generate XLSX files."""

    min_width = 8.43
    """Min width used to set column widths"""

    def header(self, content):
        self.has_header = True
        self._write_row(content, self.header_format)

    def out(self, content):
        self._write_row(content)

    def footer(self, content):
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

    def gen_tmpfilename(self):
        """It generates and returns a XLSX temporary file.

        :returns: Temporary XLSX file.
        :rtype: str"""

        return super().gen_tmpfilename() + '.xlsx'
