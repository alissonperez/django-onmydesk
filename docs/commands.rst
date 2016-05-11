Commands
==========

.. _command_process:

process
-------

Command used to process reports. E.g.::

  $ ./manage.py process

For each time you run this command it'll try to find a pending report to process. It's better to put it in a cron or something like that to run each minute.

.. _command_scheduler_process:

scheduler_process
------------------

Command used to process schedulers (see more on :doc:`schedulers`). E.g.::

  $ ./manage.py scheduler_process

For each time you call this command it'll try to find a scheduler entry for that weekday and process it. So, it's better to run it just one time in a day.
