from abc import ABCMeta, abstractmethod
from collections import OrderedDict

from django.db import connection


class BaseDataset(metaclass=ABCMeta):

    @abstractmethod
    def iterate(self):
        raise NotImplemented()

    def __enter__(self):
        return self

    def __exit__(self, type, value, traceback):
        pass


class SQLDataset(BaseDataset):

    def __init__(self, query, query_params=[]):
        self.query = query
        self.query_params = query_params

    def iterate(self):
        self.cursor.execute(self.query, self.query_params)
        one = self.cursor.fetchone()

        cols = tuple(c[0] for c in self.cursor.description)

        while one is not None:
            row = OrderedDict(zip(cols, one))
            yield row
            one = self.cursor.fetchone()

    def __enter__(self):
        self.cursor = connection.cursor()
        return self

    def __exit__(self, type, value, traceback):
        self.cursor.close()
