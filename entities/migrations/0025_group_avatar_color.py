# -*- coding: utf-8 -*-
# Generated by Django 1.9.5 on 2016-05-06 14:48
from __future__ import unicode_literals

import core.colors
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('entities', '0024_auto_20160506_1153'),
    ]

    operations = [
        migrations.AddField(
            model_name='group',
            name='avatar_color',
            field=models.CharField(default=core.colors.get_random_color, max_length=7),
        ),
    ]
