# -*- coding: utf-8 -*-
# Generated by Django 1.11.22 on 2019-11-18 09:05
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('geodatabuilder', '0003_geodatabuilder_expression_id_string'),
    ]

    operations = [
        migrations.AlterField(
            model_name='geodatabuilder',
            name='expression_id_string',
            field=models.TextField(help_text='an Expression... HELP', max_length=2000, verbose_name='expression id'),
        ),
    ]
