# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('onmydesk', '0002_auto_20160413_1435'),
    ]

    operations = [
        migrations.AddField(
            model_name='report',
            name='status',
            field=models.CharField(default='pending', max_length=20, choices=[('pending', 'Pending'), ('processing', 'Processing'), ('processed', 'Processed'), ('error', 'Error')]),
        ),
    ]
