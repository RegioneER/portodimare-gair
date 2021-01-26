# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.conf import settings
from django.db import models
from django.utils.translation import ugettext_lazy as _
from django.utils.timezone import now
from django.core.urlresolvers import reverse

# Create your models here.

class GeoDataBuilder(models.Model):
  
    expression_help_text = _(
            'an Expression... HELP')

    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        blank=False,
        null=False,
        related_name='owned_geodatabuilder',
        verbose_name=_("Owner"))
        
    label = models.CharField(
        _('label'),
        max_length=255,
        blank=False,
        null=False)
    
    desc_expression = models.TextField(
        _('expression description'),
        max_length=2000,
        blank=False,
        help_text=expression_help_text)

    expression = models.TextField(
        _('expression'),
        max_length=2000,
        blank=False,
        help_text=expression_help_text)

    expression_id_string = models.TextField(
        _('expression id'),
        max_length=2000,
        blank=False,
        help_text=expression_help_text)
    
    file_path = models.CharField(
        _('file'),
        max_length=2000,
        blank=True,
        null=True)

    file_updated = models.DateTimeField(
        _('file data update'),
        blank=True,
        null=True)
    
    casestudy_api_id = models.IntegerField(verbose_name="API Case Study ID",  null=False, serialize=False, editable=True )  
    
    created = models.DateTimeField(auto_now_add=True)

    updated = models.DateTimeField(_('last modified'), auto_now=True, help_text=_(
         'date when expression were last updated'))  # passing the method itself, not

    status = models.CharField(
        _('status'),
        max_length=128,
        blank=True,
        null=True)
    
    def __unicode__(self):
        return u"{0}".format(self.label)

    def save(self, *args, **kwargs):
        ''' On save, update timestamps '''
        self.updated = now
        return super(GeoDataBuilder, self).save(*args, **kwargs)

    class Meta:
        ordering = ("label", "created", "updated")
        verbose_name_plural = 'GeoDataBuilders'
