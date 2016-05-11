Schedulers
==========

With a scheduler we can schedule (Wow!) a generation of a report with some perioditicy automatically, like every monday or from monday to friday all the week.

Basic Usage
------------

First of all, we'll need a report to schedule. If you don't have one, create it and go back here (see more on :doc:`userguide`).

Now, to use schedulers you basically need to create a schedule entry with admin screen (see more about on :ref:`creating_schedulers`) and run command :ref:`command_scheduler_process`.

If you want to notify someone about reports generated with schedulers it's better to setup :ref:`onmydesk_notify_from` and :ref:`onmydesk_scheduler_notify_subject`.

.. _creating_schedulers:

Creating schedulers
^^^^^^^^^^^^^^^^^^^

1. Go to **Schedulers** screen in your admin screen and try to add a new schedule. You can notice this screen is very similar to report screen creation with some extra fields.

2. Select the **Report** that you want to schedule.

3. Select the **Periodicity**. You'll see some options like **Every monday** or **Monday to Friday**. This field is used to determinate which days of week your report will be generated automatically.

4. Fill **Notify e-mails** with the e-mails separated by ',' if you want to notify someone (including you).

Processing schedulers
^^^^^^^^^^^^^^^^^^^^^^

To process them we only must to run :ref:`command_scheduler_process`. It's better to setup a cron or something similar to run this command once in a day to process all schedulers that have a periodicity matching with that week day.

Schedulers for reports with parameters
---------------------------------------

We can use reports with parameters (see about on :ref:`params_from_user`) with our schedulers. Similar when we select a report on report creation screen, here when you select a report the page is reloaded and you can fill out the parameters to process your report.

Scheduling reports with date fields in parameters
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

When you select a report on a scheduler with a date field in its parameters you'll must fill this fields in a different way. Instead of selecting the exactally date you need to use **D** as a current date of report generation and subtract or add many days you need. Ok, it sounds confusing, let's go to an example:

Suposing you have a report that needs to be created every monday and builds its information with data of last week. This report should have two parameters to store this dates. When you select this report, you'll fill **start_date** with "D-7" and **end_date** with "D-1".

With this setup, running our scheduler on **May 9 2016** (this is our **D**), parameters will be with **start_date** as **May 2 2016** (**D-7**, Monday before) and **end_date** as **May 8 2106** (**D-1**, last Sunday).
