# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations


def set_actual_status(apps, schema_editor):
    Report = apps.get_model('onmydesk', 'Report')

    Report.objects.update(status='processed')


def reverse_func(apps, schema_editor):
    pass


class Migration(migrations.Migration):

    dependencies = [
        ('onmydesk', '0003_report_status'),
    ]

    operations = [
        migrations.RunPython(set_actual_status, reverse_func),
    ]
