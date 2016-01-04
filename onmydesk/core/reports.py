from abc import ABCMeta, abstractmethod

from onmydesk.core import datasets
from onmydesk.core import outputs


class BaseReport(metaclass=ABCMeta):
    name = None

    params = None
    form = None

    header = None
    footer = None

    def __init__(self, params=None):
        self.output_filepaths = []
        self.params = params

    def process(self):
        with self.dataset as ds:
            for output in self.outputs:
                output.row_cleaner = self.row_cleaner
                output.process(ds, header=self.header, footer=self.footer)
                self.output_filepaths.append(output.filepath)

    def row_cleaner(self, row):
        return row

    @classmethod
    def get_form(cls):
        return cls.form

    @property
    @abstractmethod
    def dataset(self):
        raise NotImplemented()

    @property
    @abstractmethod
    def outputs(self):
        raise NotImplemented()


class SQLReport(BaseReport):
    query = None
    query_params = []
    outputs = (outputs.TSVOutput(),)

    @property
    def dataset(self):
        return datasets.SQLDataset(self.query, self.query_params)
