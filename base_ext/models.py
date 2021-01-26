# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models

# Create your models here.
    
class MainCategory(models.Model):
    identifier = models.CharField(max_length=255, default='location')
    description = models.TextField(default='')
    gn_description = models.TextField(
        'GeoNode description', default='', null=True)
    is_choice = models.BooleanField(default=True)
    fa_class = models.CharField(max_length=64, default='fa-times')

    def __unicode__(self):
        return u"{0}".format(self.gn_description)

    class Meta:
        ordering = ("identifier",)
        verbose_name_plural = 'Main Categories'

class DomainArea(models.Model):
    identifier = models.CharField('Domain Area name', max_length=255, unique=True)
    description = models.TextField(default='')
    gn_description = models.TextField(
        'GeoNode description', default='', null=True)
    is_choice = models.BooleanField(default=True)

    def __unicode__(self):
        return u"{0}".format(self.gn_description)

    def get_self_resource(self):
        """Get associated resource base."""
        # Associate this model with resource
        try:
            resourcebase = self.resourcebase_domainarea.first()
            """:type: ResourceBase"""
            return resourcebase.get_self_resource()
        except BaseException:
            return None

    class Meta:
        ordering = ("identifier",)
        verbose_name_plural = 'Domain Areas'

class DataPortal(models.Model):
    identifier = models.CharField('Data Portal name', max_length=255, unique=True)
    description = models.TextField(default='')
    gn_description = models.TextField(
        'GeoNode description', default='', null=True)
    is_choice = models.BooleanField(default=True)

    def __unicode__(self):
        return u"{0}".format(self.gn_description)

    class Meta:
        ordering = ("identifier",)
        verbose_name_plural = 'Data Portal'

class ValidationLevel(models.Model):
    identifier = models.CharField('Validation Level name', max_length=255, unique=True)
    description = models.TextField(default='')
    gn_description = models.TextField(
        'GeoNode description', default='', null=True)
    is_choice = models.BooleanField(default=True)

    def __unicode__(self):
        return u"{0}".format(self.gn_description)

    class Meta:
        ordering = ("identifier",)
        verbose_name_plural = 'Validation Level'

class StarredForm(models.Model):
    identifier = models.BooleanField('Starred class')
