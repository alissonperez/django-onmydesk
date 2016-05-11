Settings
=========

ONMYDESK_REPORT_LIST
--------------------

It must contains a list of reports to be available at admin screen.

Example::

    ONMYDESK_REPORT_LIST = [
	# ...
        'myapp.reports.MyReport',
    ]

.. _onmydesk_file_handler:

ONMYDESK_FILE_HANDLER
------------------------

It's an optional setting. It must be used to indicate a function to be called to handle a file after its generation. This function will receive the report filepath and must return a filepath, a url or something like this. It's useful to move reports to another directory or to a cloud storage.

Example:

We create a function at any place to upload our report to an Amazon S3 bucket::

    # myapp/utils.py

    def report_s3_upload(filepath):
	bucket = get_bucket(settings.BUCKETS['reports'])

	now = timezone.now()

	key_name = '{}/{}/{}'.format(
	    now.strftime('%Y'),
	    now.strftime('%m-%d'),
	    path.basename(filepath))

	key = bucket.new_key(key_name)
	key.set_contents_from_filename(filepath)

	return key.name

On our settings, we setup with::

  ONMYDESK_FILE_HANDLER = 'myapp.utils.report_s3_upload'

Now, our reports will be uploaded to our bucket at Amazon S3 after its processing.

.. _onmydesk_download_link_handler:

ONMYDESK_DOWNLOAD_LINK_HANDLER
-------------------------------

It's an optional setting. It must be used to indicate a function to generate a link to download our report file. This function will receive the report filepath or what was returned by :ref:`onmydesk_file_handler` and must return a url to download the report file.

Example:

In the same way showed by :ref:`onmydesk_file_handler`, now our function will return a url to download our report from Amazon S3 bucket::

  # myapp/utils.py

  def get_report_s3_link(filepath):
    bucket = get_bucket(settings.BUCKETS['reports'])

    key = bucket.get_key(filepath)

    return key.generate_url(settings.REPORT_S3_LINK_LIFETIME)

On our settings, we setup with::

  ONMYDESK_DOWNLOAD_LINK_HANDLER = 'myapp.utils.get_report_s3_link'

.. _onmydesk_notify_from:

ONMYDESK_NOTIFY_FROM
---------------------

Used to fill out **from** field of sent e-mails. Default is 'no-reply@nobody.com'. E.g.::

  ONMYDESK_NOTIFY_FROM = 'no-reply@mycompany.com'

.. _onmydesk_scheduler_notify_subject:

ONMYDESK_SCHEDULER_NOTIFY_SUBJECT
----------------------------------

Used by scheduler (see more on :doc:`schedulers`) as e-mail subject. You can use `{report_name}` on your string to use report name.
Default is `OnMyDesk - Report - {report_name}`. E.g.::

  ONMYDESK_SCHEDULER_NOTIFY_SUBJECT = 'My company - Scheduled report {report_name}'
