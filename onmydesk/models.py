"""
Required models to handle and store generated reports.
"""

from django.db import models
from django.conf import settings

from timeit import default_timer as timer
from decimal import Decimal, getcontext

from onmydesk.utils import my_import

ONMYDESK_FILE_HANDLER = getattr(settings, 'ONMYDESK_FILE_HANDLER', None)


class ReportNotSavedException(Exception):
    pass


def output_file_handler(filepath):
    """
    Returns the output filepath (handled or not by an external function).
    This function tries to find a function handler in `settings.ONMYDESK_FILE_HANDLER`. It
    must receive a filepath and returns a new filepath (or url, e.g.) to be stored in the
    report register. It's useful to handle the report results (move to other dirs ou to cloud).

    :param str filepath: File path to output generated by report.
    :returns: File path to output (processed or not by a external handler)
    :rtype: str
    """

    function_handler = ONMYDESK_FILE_HANDLER

    if not function_handler:
        return filepath

    handler = my_import(function_handler)
    return handler(filepath)


class Report(models.Model):
    """Report model to store generated reports"""

    STATUS_PENDING = 'pending'
    STATUS_PROCESSING = 'processing'
    STATUS_PROCESSED = 'processed'
    STATUS_ERROR = 'error'

    STATUS_CHOICES = (
        (STATUS_PENDING, 'Pending'),
        (STATUS_PROCESSING, 'Processing'),
        (STATUS_PROCESSED, 'Processed'),
        (STATUS_ERROR, 'Error'),
    )

    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=STATUS_PENDING)
    process_time = models.DecimalField(verbose_name='Process time (secs)', max_digits=10,
                                       decimal_places=4, null=True, blank=True)

    report = models.CharField(max_length=255)
    results = models.CharField(max_length=255, null=True, blank=True)

    insert_date = models.DateTimeField('Creation Date', auto_now_add=True)
    update_date = models.DateTimeField('Update Date', auto_now=True)

    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, null=True)

    def process(self, report_params=None):
        """Process this report. After processing the outputs will be stored at `results`.
        To access output results is recommended to use :func:`results_as_list`.

        :param dict report_params: Dictionary with params to be used for process report.
        """

        if not self.id:
            raise ReportNotSavedException()

        self.status = Report.STATUS_PROCESSING
        self.save(update_fields=['status'])

        report_class = my_import(self.report)

        report = report_class(params=report_params)

        try:
            getcontext().prec = 5
            start = Decimal(timer())
            report.process()
            self.process_time = Decimal(timer()) - start

            results = []
            for filepath in report.output_filepaths:
                results.append(output_file_handler(filepath))

            self.results = ';'.join(results)

            self.status = Report.STATUS_PROCESSED
            self.save(update_fields=['status'])
        except Exception:
            self.status = Report.STATUS_ERROR
            self.save(update_fields=['status'])

    @property
    def results_as_list(self):
        """Returns a list of output results stored in this model

        :returns: List of results
        :rtype: list"""

        if not self.results:
            return []

        return self.results.split(';')
