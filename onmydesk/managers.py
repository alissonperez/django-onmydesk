from django.db import models


class SchedulerManager(models.Manager):

    def pending(self, date):
        from .models import Scheduler
        periodicities = Scheduler.PERIODICITIES_BY_WEEKDAY.get(date.weekday())
        return self.all().filter(periodicity__in=periodicities)
