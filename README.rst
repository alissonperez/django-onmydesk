Django - OnMyDesk
===================

A simple Django app to build reports.

Quick start
------------

1. Add "onmydesk" to your INSTALLED_APPS setting like this:

    INSTALLED_APPS = [
        ...
        'onmydesk',
    ]

2. Run `python manage.py migrate` to create the polls models.

4. Start the development server and visit http://127.0.0.1:8000/admin/
   to create a report (you'll need the Admin app enabled and a report class created).
