# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Report',
            fields=[
                ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True, serialize=False)),
                ('report', models.CharField(max_length=30)),
                ('results', models.CharField(max_length=255, null=True, blank=True)),
                ('insert_date', models.DateTimeField(auto_now_add=True, verbose_name='Creation Date')),
                ('update_date', models.DateTimeField(verbose_name='Update Date', auto_now=True)),
                ('created_by', models.ForeignKey(to=settings.AUTH_USER_MODEL, null=True)),
            ],
        ),
    ]
