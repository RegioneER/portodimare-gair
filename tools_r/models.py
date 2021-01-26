# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.conf import settings
from django.db import models
from django.utils.translation import ugettext_lazy as _
from django.utils.timezone import now
from django.core.urlresolvers import reverse

# Create your models here.

class ToolsR_1_8(models.Model):
    """
    MODULO TOOLS R 1.8 AZA
    """
    input_layers_help_text = _(
            'an input layers... HELP')

    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        blank=False,
        null=False,
        related_name='owned_tools_r',
        verbose_name=_("Owner"))

    label = models.CharField(
        _('label'),
        default=None,
        max_length=255,
        blank=False,
        null=False)

    input_layers = models.TextField(
        _('layers'),
        max_length=2000,
        null=False,
        blank=False,
        help_text=input_layers_help_text)
    
    input_criteria = models.TextField(
        _('criteria'),
        max_length=2000,
        default=None,
        null=False,
        blank=False)

    output_files = models.CharField(
        _('path output files'),
        max_length=255,
        blank=True)

    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(_('last modified'), auto_now=True, help_text=_(
         'date when expression were last updated'))  # passing the method itself, not

    public = models.BooleanField(default=False)

    status = models.CharField(
        _('status'),
        max_length=128,
        blank=True,
        null=True)

    type = models.IntegerField(
        _('type'),
        blank=False,
        null=False,
        default= settings.DEFAULT_CASESTUDY_TYPE_ID ) # "Default"

    def __unicode__(self):
        return u"{0}".format(self.label)

    class Meta:
        ordering = ("label", "created", "updated")
        verbose_name_plural = 'ToolsR 1.8'


class ToolsR_1_11(models.Model):
    """
    MODULO TOOLS R 1.11 SSF
    """
    input_layers_help_text = _(
            'an input layers... HELP')

    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        blank=False,
        null=False,
        related_name='owned_tools_r_1_11',
        verbose_name=_("Owner"))

    label = models.CharField(
        _('label'),
        default=None,
        max_length=255,
        blank=False,
        null=False)

    input_layers = models.TextField(
        _('layers'),
        max_length=2000,
        null=False,
        blank=False,
        help_text=input_layers_help_text)
    
    input_criteria = models.TextField(
        _('criteria'),
        max_length=2000,
        default=None,
        null=False,
        blank=False)
    
    pairwise_matrix = models.TextField(
        _('pairwise matrix'),
        max_length=2000,
        default=None,
        null=False,
        blank=False)

    fishing_gear = models.TextField(
        _('fishing gear'),
        max_length=9000,
        default=None,
        null=False,
        blank=False)

    output_files = models.CharField(
        _('path output files'),
        max_length=255,
        blank=True)

    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(_('last modified'), default=now, help_text=_(
         'date when expression were last updated'))  # passing the method itself, not

    public = models.BooleanField(default=False)

    status = models.CharField(
        _('status'),
        max_length=128,
        blank=True,
        null=True)

    type = models.IntegerField(
        _('type'),
        blank=False,
        null=False,
        default= settings.DEFAULT_CASESTUDY_TYPE_ID ) # "Default"


    def __unicode__(self):
        return u"{0}".format(self.label)

    class Meta:
        ordering = ("label", "created", "updated")
        verbose_name_plural = 'ToolsR 1.11'


class ToolsR_1_12(models.Model):
    """
    MODULO TOOLS R 1.12 MSF
    """
    input_layers_help_text = _(
            'an input layers... HELP')

    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        blank=False,
        null=False,
        related_name='owned_tools_r_1_12',
        verbose_name=_("Owner"))

    label = models.CharField(
        _('label'),
        default=None,
        max_length=255,
        blank=False,
        null=False)

    input_layers = models.TextField(
        _('layers'),
        max_length=2000,
        null=False,
        blank=False,
        help_text=input_layers_help_text)
    
    input_criteria = models.TextField(
        _('criteria'),
        max_length=2000,
        default=None,
        null=False,
        blank=False)
    
    pairwise_matrix_ps = models.TextField(
        _('pairwise matrix ps'),
        max_length=2000,
        default=None,
        null=False,
        blank=False)
    
    pairwise_matrix_tr = models.TextField(
        _('pairwise matrix tr'),
        max_length=2000,
        default=None,
        null=False,
        blank=False)

    fishing_gear_ps = models.TextField(
        _('fishing gear ps'),
        max_length=9000,
        default=None,
        null=False,
        blank=False)
    
    fishing_gear_tr1224 = models.TextField(
        _('fishing gear tr1224'),
        max_length=9000,
        default=None,
        null=False,
        blank=False)
    
    fishing_gear_tr2440 = models.TextField(
        _('fishing gear tr2440'),
        max_length=9000,
        default=None,
        null=False,
        blank=False)

    output_files = models.CharField(
        _('path output files'),
        max_length=255,
        blank=True)

    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(_('last modified'), default=now, help_text=_(
         'date when expression were last updated'))  # passing the method itself, not

    public = models.BooleanField(default=False)

    status = models.CharField(
        _('status'),
        max_length=128,
        blank=True,
        null=True)


    type = models.IntegerField(
        _('type'),
        blank=False,
        null=False,
        default= settings.DEFAULT_CASESTUDY_TYPE_ID ) # "Default"

    def __unicode__(self):
        return u"{0}".format(self.label)

    class Meta:
        ordering = ("label", "created", "updated")
        verbose_name_plural = 'ToolsR 1.12'