import tempfile
import csv

from uuid import uuid4
from abc import ABCMeta, abstractmethod


class BaseOutput(metaclass=ABCMeta):

    def __init__(self):
        self.filepath = None
        self.row_cleaner = None

    @abstractmethod
    def process(self, dataset, header=None, footer=None):
        raise NotImplemented()

    def gen_tmpfilename(self):
        return tempfile.gettempdir() + '/' + uuid4().hex


class TSVOutput(BaseOutput):

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
        return super().gen_tmpfilename() + '.tsv'


class CSVOutput(BaseOutput):

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
        return super().gen_tmpfilename() + '.csv'
