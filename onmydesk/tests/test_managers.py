from datetime import date
from django.test import TestCase

from onmydesk.models import Scheduler


class SchedulerManagerTestCase(TestCase):

    def test_pending_with_date_as_monday_must_return_monday_schedulers(self):
        mon_sched = self._create_with_periodicity(Scheduler.PER_MON)
        tue_sched = self._create_with_periodicity(Scheduler.PER_TUE)

        # Monday date
        mon_date = date(2016, 5, 9)

        result = Scheduler.objects.pending(mon_date)

        self.assertIn(mon_sched, result)
        self.assertNotIn(tue_sched, result)

    def test_pending_with_any_weekday_must_return_mon_to_sun_schedulers(self):
        mon_sun_sched = self._create_with_periodicity(Scheduler.PER_MON_SUN)

        mon_date = date(2016, 5, 9)
        tue_date = date(2016, 5, 10)
        wed_date = date(2016, 5, 11)
        tue_date = date(2016, 5, 12)
        fri_date = date(2016, 5, 13)
        sat_date = date(2016, 5, 14)
        sun_date = date(2016, 5, 15)

        self.assertIn(mon_sun_sched, Scheduler.objects.pending(mon_date))
        self.assertIn(mon_sun_sched, Scheduler.objects.pending(tue_date))
        self.assertIn(mon_sun_sched, Scheduler.objects.pending(wed_date))
        self.assertIn(mon_sun_sched, Scheduler.objects.pending(tue_date))
        self.assertIn(mon_sun_sched, Scheduler.objects.pending(fri_date))
        self.assertIn(mon_sun_sched, Scheduler.objects.pending(sat_date))
        self.assertIn(mon_sun_sched, Scheduler.objects.pending(sun_date))

    def test_pending_with_workday_must_return_mon_to_fri_schedulers(self):
        mon_fri_sched = self._create_with_periodicity(Scheduler.PER_MON_FRI)

        mon_date = date(2016, 5, 9)
        tue_date = date(2016, 5, 10)
        wed_date = date(2016, 5, 11)
        tue_date = date(2016, 5, 12)
        fri_date = date(2016, 5, 13)
        sat_date = date(2016, 5, 14)
        sun_date = date(2016, 5, 15)

        self.assertIn(mon_fri_sched, Scheduler.objects.pending(mon_date))
        self.assertIn(mon_fri_sched, Scheduler.objects.pending(tue_date))
        self.assertIn(mon_fri_sched, Scheduler.objects.pending(wed_date))
        self.assertIn(mon_fri_sched, Scheduler.objects.pending(tue_date))
        self.assertIn(mon_fri_sched, Scheduler.objects.pending(fri_date))
        self.assertNotIn(mon_fri_sched, Scheduler.objects.pending(sat_date))
        self.assertNotIn(mon_fri_sched, Scheduler.objects.pending(sun_date))

    def _create_with_periodicity(self, per):
        sched = Scheduler(report='some-repo',
                          periodicity=per,)
        sched.save()

        return sched
