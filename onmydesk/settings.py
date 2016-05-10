'''Local settings with default values'''

from django.conf import settings


ONMYDESK_REPORT_LIST = getattr(settings, 'ONMYDESK_REPORT_LIST', [])

ONMYDESK_DOWNLOAD_LINK_HANDLER = getattr(settings, 'ONMYDESK_DOWNLOAD_LINK_HANDLER', None)

ONMYDESK_FILE_HANDLER = getattr(settings, 'ONMYDESK_FILE_HANDLER', None)

# E-mail notification
ONMYDESK_NOTIFY_FROM = getattr(
    settings, 'ONMYDESK_NOTIFY_FROM',
    'no-reply@nobody.com')
ONMYDESK_SCHEDULER_NOTIFY_SUBJECT = getattr(
    settings, 'ONMYDESK_SCHEDULER_NOTIFY_SUBJECT',
    'OnMyDesk - Report - {report_name}')
