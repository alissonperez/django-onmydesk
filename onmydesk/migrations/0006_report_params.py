# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('onmydesk', '0005_report_process_time'),
    ]

    operations = [
        migrations.AddField(
            model_name='report',
            name='params',
            field=models.BinaryField(blank=True, null=True, verbose_name='Report params'),
        ),
    ]
