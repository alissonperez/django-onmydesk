DEBUG = True

DATABASES = {'default': {'ENGINE': 'django.db.backends.sqlite3'}}

INSTALLED_APPS = (
    # Required from
    'django.contrib.auth',
    'django.contrib.contenttypes',

    'onmydesk',
)

SECRET_KEY = 'abcde12345'

ONMYDESK_DOWNLOAD_LINK_HANDLER=None
