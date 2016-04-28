# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('onmydesk', '0004_auto_20160428_1503'),
    ]

    operations = [
        migrations.AddField(
            model_name='report',
            name='process_time',
            field=models.DecimalField(verbose_name='Process time (secs)', max_digits=10, null=True, blank=True, decimal_places=4),
        ),
    ]
