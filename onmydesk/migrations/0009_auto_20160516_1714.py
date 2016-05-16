# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('onmydesk', '0008_scheduler_notify_emails'),
    ]

    operations = [
        migrations.AlterField(
            model_name='scheduler',
            name='notify_emails',
            field=models.CharField(blank=True, verbose_name='E-mail\'s to notify after process (separated by ",")', max_length=1000, null=True),
        ),
    ]
