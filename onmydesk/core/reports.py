from abc import ABCMeta, abstractmethod

from onmydesk.core import datasets
from onmydesk.core import outputs


class BaseReport(metaclass=ABCMeta):
    """An abstract representation of a report."""

    name = None
    """Report name. E.g.: *Monthly sales*."""

    form = None
    """Django form class to enable user to fill some param."""

    params = None
    """Report params, it's used to process report."""

    header = None
    """Report header."""

    footer = None
    """Report footer."""

    output_filepaths = []
    """Output files filled by :func:`process`."""

    def __init__(self, params=None):
        """
        :param dict params: Params to be used by report (a date range to
        fetch data from database, for example).
        """

        self.output_filepaths = []
        self.params = params

    def process(self):
        """Process report and store output filepaths in :attr:`output_filepaths`"""

        with self.dataset as ds:
            for output in self.outputs:
                output.row_cleaner = self.row_cleaner
                output.process(ds, header=self.header, footer=self.footer)
                self.output_filepaths.append(output.filepath)

    def row_cleaner(self, row):
        """
        Method used to handle line by line of the report. It's useful to convert some data or do some sanitization.

        :param row: Line to be rendered in the report.
        :returns: Line after some processing with it.
        """

        return row

    @classmethod
    def get_form(cls):
        """
        :returns: Form to be used with this report in admin creation screen.
        """

        return cls.form

    @property
    @abstractmethod
    def dataset(self):
        """
        :returns: Dataset to be used by this report.
        """

        raise NotImplemented()

    @property
    @abstractmethod
    def outputs(self):
        """
        :returns: A list of outputs to be used by this report.
        """

        raise NotImplemented()


class SQLReport(BaseReport):
    """
    Report to be used with raw SQL's.

    E.g.::

        class SalesReport(SQLReport):
            query = 'SELECT * FROM sales'

        report = SalesReport()
        report.process()

        print(report.output_filepaths) # --> Files with all rows from sales table.
    """

    query = None
    """Raw report query."""

    query_params = []
    """Params to be evaluated with query."""

    outputs = (outputs.TSVOutput(),)
    """Outputs list, default TSV."""

    @property
    def dataset(self):
        return datasets.SQLDataset(self.query, self.query_params)
