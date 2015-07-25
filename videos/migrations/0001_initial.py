# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Project',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('title', models.CharField(max_length=120)),
                ('description', models.TextField(max_length=5000, null=True, blank=True)),
                ('image', models.ImageField(null=True, upload_to=b'images/', blank=True)),
                ('slug', models.SlugField(default=b'abc', unique=True)),
                ('active', models.BooleanField(default=True)),
                ('featured', models.BooleanField(default=False)),
                ('timestamp', models.DateTimeField(auto_now_add=True)),
                ('updated', models.DateTimeField(auto_now=True)),
            ],
            options={
                'ordering': ['title', 'timestamp'],
            },
        ),
        migrations.CreateModel(
            name='Video',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('title', models.CharField(max_length=120)),
                ('embed_code', models.CharField(max_length=500, null=True, blank=True)),
                ('share_message', models.TextField(default=b'Hello World~! Check out this awesome project step by step~!')),
                ('order', models.PositiveIntegerField(default=1)),
                ('slug', models.SlugField(null=True, blank=True)),
                ('active', models.BooleanField(default=True)),
                ('featured', models.BooleanField(default=False)),
                ('free_preview', models.BooleanField(default=False)),
                ('timestamp', models.DateTimeField(auto_now_add=True, null=True)),
                ('updated', models.DateTimeField(auto_now=True, null=True)),
                ('proj', models.ForeignKey(blank=True, to='videos.Project', null=True)),
            ],
            options={
                'ordering': ['order', '-timestamp'],
            },
        ),
        migrations.AlterUniqueTogether(
            name='video',
            unique_together=set([('slug', 'proj')]),
        ),
    ]
