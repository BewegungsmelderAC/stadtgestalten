# -*- coding: utf-8 -*-
# Generated by Django 1.10.5 on 2017-01-12 09:41
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('entities', '0051_auto_20170112_0956'),
        ('gestalten', '0002_auto_20170112_0847'),
        ('groups', '0005_auto_20170112_1000'),
        ('memberships', '0011_auto_20170112_0944'),
        ('subscriptions', '0009_auto_20170112_1000'),
        ('texts', '0004_auto_20170112_1000'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='gestalt',
            name='user',
        ),
        migrations.DeleteModel(
            name='Gestalt',
        ),
    ]