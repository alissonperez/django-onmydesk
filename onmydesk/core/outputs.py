import tempfile
import csv

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
    def process(self, dataset, header=None, footer=None):
        """Process the output given a `dataset`, `header` and `footer`. The result are stored in :attr:`filepath`.

        :param Dataset dataset: A dataset to be used by output.
        :param header: Output header.
        :param footer: Output footer.
        """
        raise NotImplemented()

    def gen_tmpfilename(self):
        """Utility to be used to generate a temporary filename.

        :returns: Temporary filepath.
        :rtype: str"""
        return tempfile.gettempdir() + '/' + uuid4().hex


class TSVOutput(BaseOutput):
    """An output to generate TSV files (files with cols separated by tabs)."""

    def process(self, dataset, header=None, footer=None):
        self.filepath = self.gen_tmpfilename()

        tmpfile = open(self.filepath, 'w+')
        with tmpfile:
            if header:
                rowstr = '\t'.join([str(i) for i in header])
                tmpfile.write(rowstr + '\n')

            for row in dataset.iterate():
                if self.row_cleaner:
                    row = self.row_cleaner(row)

                if isinstance(row, dict):
                    rowstr = '\t'.join([str(i) for i in row.values()])
                else:
                    rowstr = '\t'.join([str(i) for i in row])

                tmpfile.write(rowstr + '\n')

            if footer:
                rowstr = '\t'.join([str(i) for i in footer])
                tmpfile.write(rowstr + '\n')

    def gen_tmpfilename(self):
        """It generates and returns a tsv temporary file.

        :returns: Temporary TSV file.
        :rtype: str"""

        return super().gen_tmpfilename() + '.tsv'


class CSVOutput(BaseOutput):
    """An output to generate CSV files (files with cols separated by comma)."""

    def process(self, dataset, header=None, footer=None):
        self.filepath = self.gen_tmpfilename()

        tmpfile = open(self.filepath, 'w+')
        with tmpfile:
            writer = csv.writer(tmpfile)

            if header:
                writer.writerow([str(i) for i in header])

            for row in dataset.iterate():
                if self.row_cleaner:
                    row = self.row_cleaner(row)

                if isinstance(row, dict):
                    writer.writerow([str(a) for a in row.values()])
                else:
                    writer.writerow([str(b) for b in row])

            if footer:
                writer.writerow([str(c) for c in footer])

        return None

    def gen_tmpfilename(self):
        """It generates and returns a CSV temporary file.

        :returns: Temporary CSV file.
        :rtype: str"""

        return super().gen_tmpfilename() + '.csv'
