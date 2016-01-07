User guide
==========

Installation
------------

With pip over ssh::

  pip install -e git+git@github.com:knowledge4life/django-onmydesk.git@develop#egg=django-onmydesk

Or with requirements.txt file::

  -e git+git@github.com:knowledge4life/django-onmydesk.git@master#egg=django-onmydesk

Add 'onmydesk' to your INSTALLED_APPS::

  INSTALLED_APPS = [
      # ...
      'onmydesk',
  ]

Run `./manage.py migrate` to create **OnMyDesk** models.

Quickstart
-----------

To create reports we need to follow just two steps:

    1. Create a report class in our django app.
    2. Add this report class to a config in you project settings to enable **OnMyDesk** to see your reports.

So, let's do it!

Create a module called *reports.py* in you django app with the following content:

myapp/reports.py::

    from reports.core import reports

    class UsersReport(reports.SQLReport):
        name = 'Users report'
	query = 'SELECT * FROM auth_user'

On your project settings, add the following config::

    ONMYDESK_REPORT_LIST = [
	'myapp.reports.UsersReport',
    ]

**PS.: Each new report must be added to this list. Otherwise, it won't be shown on admin screen.**

Now, access your **OnMyDesk** admin screen and you'll see your **Users report** available on report creation screen.

A little bit more
------------------

Parameters from user
^^^^^^^^^^^^^^^^^^^^^

Sometimes we need to get some info from user, like a date range, a category or something like this.

To do this, we can create a Django form to our report that will be showed to users in report selection on admin screen. After this, users will fill the form and the validated params will be available at report params attribute.

For example, with this changes our *report.py* should be like this::

    from reports.core import reports

    from django import forms
    from django.contrib.admin.widgets import AdminDateWidget


    class UsersForm(forms.Form):
	start_date = forms.DateField(widget=AdminDateWidget)
	end_date = forms.DateField(widget=AdminDateWidget)


    class UsersReport(reports.SQLReport):
	form = UsersForm

	name = 'Users report'

	query = 'SELECT * FROM auth_user WHERE date_joined between %s and %s'

	@property
	def query_params(self):
	    return [
		self.params['start_date'],
		self.params['end_date']
	    ]

PS.: We have a property called `query_params` in SQLReport that must return the params to be used in our query.

Other ways to get data
^^^^^^^^^^^^^^^^^^^^^^^

We aren't restricted by raw database sql queries (and we know that, by some reasons, it is not a good way to get our report data).

Reports in **OnMyDesk** are composed by Datasets and Outputs (we'll take a better look on both ahead). So, if you need to get your data by your own way you can create a Dataset. E.g.::

    from reports.core import reports, datasets, outputs


    class TotalsDataset(datasets.BaseDataset):

	def iterate(self):
	    return [
		('Users', self._get_total_users()),
		('Premium users', self._get_total_premium_users()),
	    ]

	def _get_total_users(self):
	    return 42  # Get your number from some source...

	def _get_total_premium_users(self):
	    return 32  # Get your number from some source...


    class TotalsReport(reports.BaseReport):
	name = 'Users - Totals'

	# Our report must be a csv file
	outputs = (outputs.CSVOutput(),)

	# An instance from our dataset
	dataset = TotalsDataset()

We just need to return an interable object in iterate method from our dataset.


Settings
---------

ONMYDESK_REPORT_LIST
^^^^^^^^^^^^^^^^^^^^^^

It must contains a list of reports to be available at admin screen.

Example::

    ONMYDESK_REPORT_LIST = [
	# ...
        'myapp.reports.MyReport',
    ]

.. _onmydesk_file_handler:

ONMYDESK_FILE_HANDLER
^^^^^^^^^^^^^^^^^^^^^

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
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

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
