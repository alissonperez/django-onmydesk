from abc import ABCMeta, abstractmethod
from collections import OrderedDict

from django.db import connection, connections


class BaseDataset(metaclass=ABCMeta):
    """An abstract representation of what must be a Dataset class.

    It's possible to use context management with datasets. To do this you must
    override methods :func:`__enter__` to lock resources and :func:`__exit__` to free up them. E.g.::

        class MyDataset(BaseDataset):
            def iterate(self, params=None):
                return self.file.read()

            def __enter__(self):
                self.file = open('somefile.txt')

            def __exit__(self, type, value, traceback):
                self.file.close()

        with MyDataset() as mydataset:
            for row in mydataset.iterate():
                print(row)
    """

    @abstractmethod
    def iterate(self, params=None):
        """It must returns any iterable object.

        :param dict params: Parameters to be used by dataset"""

        raise NotImplemented()

    def __enter__(self):
        """*Enter* from context manager to lock some resource (for example)."""
        return self

    def __exit__(self, type, value, traceback):
        """*Exit* from context manager to free up some resource (for example)."""
        pass


class SQLDataset(BaseDataset):
    """
    A SQLDataset is used to run raw queries into database. E.g.::

        with SQLDataset('SELECT * FROM users'):
            for row in mydataset.iterate():
                print(row)   # --> A OrderedDict with cols and values.

    .. note:: It's recomended to use instances of this class using `with` statement.

    **BE CAREFUL**

    Always use `query_params` from :func:`__init__` to put dinamic values into the query. E.g.::

            # WRONG WAY:
            mydataset = SQLDataset('SELECT * FROM users where age > {}'.format(18))

            # RIGHT WAY:
            mydataset = SQLDataset('SELECT * FROM users where age > %d', [18])

    """

    def __init__(self, query, query_params=[], db_alias=None):
        """
        :param str query: Raw sql query.
        :param list query_params: Params to be evaluated with query.
        :param str db_alias: Database alias from django settings. Optional.
        """

        self.query = query
        self.query_params = query_params
        self.db_alias = db_alias
        self.cursor = None

    def iterate(self, params=None):
        """
        :param dict params: Parameters to be used by dataset.
        :returns: Rows from query result.
        :rtype: Iterator with OrderedDict items.
        """

        # Used if we are not using context manager
        has_cursor = bool(self.cursor)
        if not has_cursor:
            self._init_cursor()

        self.cursor.execute(self.query, self.query_params)
        cols = tuple(c[0] for c in self.cursor.description)

        one = self.cursor.fetchone()
        while one is not None:
            row = OrderedDict(zip(cols, one))
            yield row
            one = self.cursor.fetchone()

        if not has_cursor:
            self._close_cursor()

    def __enter__(self):
        """*Enter* from context manager to open a cursor with database"""
        self._init_cursor()
        return self

    def __exit__(self, type, value, traceback):
        """*Exit* from context manager to close cursor with database"""
        self._close_cursor()

    def _close_cursor(self):
        self.cursor.close()
        self.cursor = None

    def _init_cursor(self):
        if self.db_alias:
            self.cursor = connections[self.db_alias].cursor()
        else:
            self.cursor = connection.cursor()
