# -*- coding: utf-8 -*-
# Generated by Django 1.11.22 on 2019-09-11 17:31
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='DataPortal',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('identifier', models.CharField(max_length=255, unique=True, verbose_name='Data Portal name')),
                ('description', models.TextField(default='')),
                ('gn_description', models.TextField(default='', null=True, verbose_name='GeoNode description')),
                ('is_choice', models.BooleanField(default=True)),
            ],
            options={
                'ordering': ('identifier',),
                'verbose_name_plural': 'Data Portal',
            },
        ),
        migrations.CreateModel(
            name='DomainArea',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('identifier', models.CharField(default='', max_length=255, unique=True, verbose_name='Domain Area name')),
                ('description', models.TextField(default='')),
                ('gn_description', models.TextField(default='', null=True, verbose_name='GeoNode description')),
                ('is_choice', models.BooleanField(default=True)),
            ],
            options={
                'ordering': ('identifier',),
                'verbose_name_plural': 'Domain Areas',
            },
        ),
        migrations.CreateModel(
            name='MainCategory',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('identifier', models.CharField(default='location', max_length=255)),
                ('description', models.TextField(default='')),
                ('gn_description', models.TextField(default='', null=True, verbose_name='GeoNode description')),
                ('is_choice', models.BooleanField(default=True)),
                ('fa_class', models.CharField(default='fa-times', max_length=64)),
            ],
            options={
                'ordering': ('identifier',),
                'verbose_name_plural': 'Main Categories',
            },
        ),
        migrations.CreateModel(
            name='ValidationLevel',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('identifier', models.CharField(max_length=255, unique=True, verbose_name='Validation Level name')),
                ('description', models.TextField(default='')),
                ('gn_description', models.TextField(default='', null=True, verbose_name='GeoNode description')),
                ('is_choice', models.BooleanField(default=True)),
            ],
            options={
                'ordering': ('identifier',),
                'verbose_name_plural': 'Validation Level',
            },
        ),
    ]
