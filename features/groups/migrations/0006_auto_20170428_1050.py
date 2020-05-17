# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2017-04-28 08:50
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('gestalten', '0006_gestaltsetting'),
        ('memberships', '0011_auto_20170112_0944'),
        ('groups', '0005_auto_20170112_1000'),
    ]

    operations = [
        migrations.AddField(
            model_name='group',
            name='members',
            field=models.ManyToManyField(through='memberships.Membership', to='gestalten.Gestalt'),
        ),
        migrations.AlterField(
            model_name='group',
            name='gestalt_created',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='+', to='gestalten.Gestalt'),
        ),
    ]