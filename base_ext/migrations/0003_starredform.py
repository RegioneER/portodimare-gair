# -*- coding: utf-8 -*-
# Generated by Django 1.11.28 on 2020-12-21 08:11
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('base_ext', '0002_auto_20191205_1416'),
    ]

    operations = [
        migrations.CreateModel(
            name='StarredForm',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('identifier', models.BooleanField(verbose_name='Starred class')),
            ],
        ),
    ]
