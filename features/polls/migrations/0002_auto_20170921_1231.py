# -*- coding: utf-8 -*-
# Generated by Django 1.11.5 on 2017-09-21 10:31
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('polls', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='EventOption',
            fields=[
                ('option_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='polls.Option')),
                ('time', models.DateTimeField()),
                ('until_time', models.DateTimeField(blank=True, null=True)),
            ],
            options={
                'abstract': False,
            },
            bases=('polls.option',),
        ),
        migrations.CreateModel(
            name='SimpleOption',
            fields=[
                ('option_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='polls.Option')),
                ('title2', models.CharField(max_length=255)),
            ],
            options={
                'abstract': False,
            },
            bases=('polls.option',),
        ),
        migrations.RemoveField(
            model_name='option',
            name='title',
        ),
    ]
