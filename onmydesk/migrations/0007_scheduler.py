# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('onmydesk', '0006_report_params'),
    ]

    operations = [
        migrations.CreateModel(
            name='Scheduler',
            fields=[
                ('id', models.AutoField(serialize=False, verbose_name='ID', primary_key=True, auto_created=True)),
                ('report', models.CharField(max_length=255)),
                ('periodicity', models.CharField(max_length=20, choices=[('mon_fri', 'Monday to Friday'), ('mon_sun', 'Monday to Sunday'), ('sun', 'Every Sunday'), ('mon', 'Every Monday'), ('tue', 'Every Tuesday'), ('wed', 'Every Wednesday'), ('thu', 'Every Thursday'), ('fri', 'Every Friday'), ('sat', 'Every Saturday')])),
                ('params', models.BinaryField(verbose_name='Parameters', blank=True, null=True)),
                ('insert_date', models.DateTimeField(verbose_name='Creation Date', auto_now_add=True)),
                ('update_date', models.DateTimeField(verbose_name='Update Date', auto_now=True)),
                ('created_by', models.ForeignKey(to=settings.AUTH_USER_MODEL, null=True)),
            ],
        ),
    ]
