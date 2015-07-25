# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import datetime
from django.utils.timezone import utc
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        ('contenttypes', '0002_remove_content_type_name'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='PageView',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('path', models.CharField(max_length=350)),
                ('primary_object_id', models.PositiveIntegerField(null=True, blank=True)),
                ('secondary_object_id', models.PositiveIntegerField(null=True, blank=True)),
                ('timestamp', models.DateTimeField(default=datetime.datetime(2015, 7, 23, 2, 46, 13, 646483, tzinfo=utc))),
                ('primary_content_type', models.ForeignKey(related_name='primary_obj', blank=True, to='contenttypes.ContentType', null=True)),
                ('secondary_content_type', models.ForeignKey(related_name='secondary_obj', blank=True, to='contenttypes.ContentType', null=True)),
                ('user', models.ForeignKey(blank=True, to=settings.AUTH_USER_MODEL, null=True)),
            ],
            options={
                'ordering': ['-timestamp'],
            },
        ),
    ]
