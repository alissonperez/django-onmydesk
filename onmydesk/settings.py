'''Local settings with default values'''

from django.conf import settings


ONMYDESK_REPORT_LIST = getattr(settings, 'ONMYDESK_REPORT_LIST', [])

ONMYDESK_DOWNLOAD_LINK_HANDLER = getattr(settings, 'ONMYDESK_DOWNLOAD_LINK_HANDLER', None)

ONMYDESK_FILE_HANDLER = getattr(settings, 'ONMYDESK_FILE_HANDLER', None)
