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
        self.row_cleaner = None

    @abstractmethod
    def process(self, iterator, header=None, footer=None):
        """Process the output given a `dataset`, `header` and `footer`. The result are stored in :attr:`filepath`.

        :param iterator iterator: A iterable object.
        :param header: Output header.
        :param footer: Output footer.
        """
        raise NotImplemented()

    def gen_tmpfilename(self):
        """Utility to be used to generate a temporary filename.

        :returns: Temporary filepath.
        :rtype: str"""
        return tempfile.gettempdir() + '/' + uuid4().hex


class SVOutput(BaseOutput, metaclass=ABCMeta):
    '''Abstract separated values output'''

    delimiter = None

    def process(self, iterator, header=None, footer=None):
        """Process the output given a `dataset`, `header` and `footer`. The result are stored in :attr:`filepath`.

        :param Dataset dataset: A dataset to be used by output.
        :param header: Output header.
        :param footer: Output footer.
        """

        self.filepath = self.gen_tmpfilename()

        tmpfile = open(self.filepath, 'w+')
        with tmpfile:
            writer = csv.writer(tmpfile, delimiter=self.delimiter)

            if header:
                writer.writerow([str(i) for i in header])

            for row in iterator:
                if self.row_cleaner:
                    row = self.row_cleaner(row)

                if isinstance(row, dict):
                    writer.writerow([str(a) for a in row.values()])
                else:
                    writer.writerow([str(b) for b in row])

            if footer:
                writer.writerow([str(c) for c in footer])

        return None


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

    def process(self, iterator, header=None, footer=None):
        """Process the output given a `dataset`, `header` and `footer`. The result are stored in :attr:`filepath`.

        :param Dataset dataset: A dataset to be used by output.
        :param header: Output header.
        :param footer: Output footer.
        """

        self.filepath = self.gen_tmpfilename()
        workbook = xlsxwriter.Workbook(self.filepath)
        worksheet = workbook.add_worksheet()

        header_format = workbook.add_format({'bold': True, 'bg_color': '#C9C9C9'})
        footer_format = workbook.add_format({'bold': True, 'bg_color': '#DDDDDD'})

        current_row = 0
        if header:
            worksheet.write_row(current_row, 0, [str(i) for i in header], header_format)
            current_row += 1

        for row_num, row in enumerate(iterator, start=current_row):
            if self.row_cleaner:
                row = self.row_cleaner(row)

            if isinstance(row, dict):
                values = [a for a in row.values()]
            else:
                values = [b for b in row]

            worksheet.write_row(row_num, 0, values)

            current_row = row_num

        if footer:
            current_row += 1
            worksheet.write_row(current_row, 0, [str(i) for i in footer], footer_format)

        workbook.close()

    def gen_tmpfilename(self):
        """It generates and returns a XLSX temporary file.

        :returns: Temporary XLSX file.
        :rtype: str"""

        return super().gen_tmpfilename() + '.xlsx'
