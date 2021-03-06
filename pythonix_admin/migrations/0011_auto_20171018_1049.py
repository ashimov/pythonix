# -*- coding: utf-8 -*-
# Generated by Django 1.11.6 on 2017-10-18 10:49
from __future__ import unicode_literals

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('pythonix_admin', '0010_auto_20171018_1011'),
    ]

    operations = [
        migrations.AddField(
            model_name='deferredactionswithclient',
            name='scheduled_implementation_date',
            field=models.DateField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='clients',
            name='end_used_date',
            field=models.DateField(default=datetime.datetime(2017, 10, 21, 10, 49, 46, 280036), verbose_name='Дата окончяния услуги'),
        ),
        migrations.AlterField(
            model_name='temporarypay',
            name='del_pay',
            field=models.DateField(default=datetime.datetime(2017, 10, 21, 10, 49, 46, 285540), verbose_name='Дата удаления временного платежа'),
        ),
    ]
