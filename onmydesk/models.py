from django.db import models
from django.conf import settings

from reports.utils import my_import


def output_file_handler(filepath):
    function_handler = getattr(settings, 'REPORT_FILE_HANDLER', None)

    if not function_handler:
        return filepath

    handler = my_import(function_handler)
    return handler(filepath)


class Report(models.Model):
    report = models.CharField(max_length=30)
    results = models.CharField(max_length=255, null=True, blank=True)

    insert_date = models.DateTimeField('Creation Date', auto_now_add=True)
    update_date = models.DateTimeField('Update Date', auto_now=True)

    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, null=True)

    def process(self, report_params=None):
        report_class = my_import(self.report)

        report = report_class(params=report_params)
        report.process()

        results = []
        for filepath in report.output_filepaths:
            results.append(output_file_handler(filepath))

        self.results = ';'.join(results)

    @property
    def results_as_list(self):
        if not self.results:
            return []

        return self.results.split(';')
