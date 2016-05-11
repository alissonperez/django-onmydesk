User guide
==========

Installation
------------

With pip over ssh::

  pip install -e git+git@github.com:knowledge4life/django-onmydesk.git@master#egg=django-onmydesk

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

    from onmydesk.core import reports

    class UsersReport(reports.SQLReport):
        name = 'Users report'
	query = 'SELECT * FROM auth_user'

On your project settings, add the following config::

    ONMYDESK_REPORT_LIST = [
	'myapp.reports.UsersReport',
    ]

.. note::
   Each new report must be added to this list. Otherwise, it won't be shown on admin screen.

Now, access your **OnMyDesk** admin screen and you'll see your **Users report** available on report creation screen.

After you create a report, it'll be status settled up as 'Pending', to process it you must run :ref:`command_process` command. E.g::

  $ ./manage.py process
  Found 1 reports to process
  Processing report #29 - 1 of 1
  Report #29 processed
  $

A little bit more
------------------

.. _params_from_user:

Parameters from user
^^^^^^^^^^^^^^^^^^^^^

Sometimes we need to get some info from user, like a date range, a category or something like this.

To do this, we can create a Django form to our report that will be showed to users in report selection on admin screen. After this, users will fill the form and the validated params will be available at report params attribute.

For example, with this changes our *report.py* should be like this::

    from onmydesk.core import reports

    from django import forms
    from django.contrib.admin.widgets import AdminDateWidget


    class UsersForm(forms.Form):
	start_date = forms.DateField(widget=AdminDateWidget)
	end_date = forms.DateField(widget=AdminDateWidget)


    class UsersReport(reports.SQLReport):
	form = UsersForm

	name = 'Users report'

	query = 'SELECT * FROM auth_user WHERE date_joined between %s and %s'

	# Optionally we can use a db alias to change our database.
	db_alias = 'my-other-database'

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

    from onmydesk.core import reports, datasets, outputs


    class TotalsDataset(datasets.BaseDataset):

	def iterate(self, params=None):
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

Changing report's outputs
^^^^^^^^^^^^^^^^^^^^^^^^^

We can change the output of our report. The easier way to do this is to change `outputs` attribute of our report class.

Example::

    class TotalsReport(reports.BaseReport):
	name = 'Users - Totals'

	# Changing our outputs to TSV and XLSx
	outputs = (outputs.TSVOutput(), outputs.XLSXOutput())

We have some output options by default. See more about on :py:mod:`onmydesk.core.outputs`.
