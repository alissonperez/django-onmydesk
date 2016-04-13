# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('onmydesk', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='report',
            name='report',
            field=models.CharField(max_length=255),
        ),
    ]
