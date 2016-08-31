# -*- coding: utf-8 -*-
# Generated by Django 1.9.7 on 2016-08-11 14:05
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


def set_created_by(apps, schema_editor):
    Membership = apps.get_model('memberships', 'Membership')
    for m in Membership.objects.all():
        m.created_by = m.member
        m.save()


class Migration(migrations.Migration):

    dependencies = [
        ('entities', '0042_group_closed'),
        ('memberships', '0004_auto_20160724_1659'),
    ]

    operations = [
        migrations.AddField(
            model_name='membership',
            name='created_by',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='memberships_created', to='entities.Gestalt'),
        ),
        migrations.AlterField(
            model_name='membership',
            name='member',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='memberships', to='entities.Gestalt'),
        ),
        migrations.RunPython(set_created_by),
    ]