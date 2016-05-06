# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('onmydesk', '0007_scheduler'),
    ]

    operations = [
        migrations.AddField(
            model_name='scheduler',
            name='notify_emails',
            field=models.CharField(null=True, blank=True, max_length=1000, verbose_name="E-mail's to notify after process"),
        ),
    ]
