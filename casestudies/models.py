# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models

# Create your models here.
from geonode.base.models import ResourceBase
from geonode.groups.models import GroupProfile
from django.db.models.signals import post_save
from django.dispatch import receiver
#import uuid
# from rest_framework import serializers

from django.contrib.auth import get_user_model

class CasestudiesModule(models.Model):
    """
    LISTA DEI MODULI CASE STUDIES
    """
    # group = models.ForeignKey(GroupProfile, related_name='group_collections')
    # resources = models.ManyToManyField(ResourceBase, related_name='resource_collections')
    name = models.CharField(max_length=128, unique=True)
    slug = models.SlugField(max_length=128, unique=True)

    def __unicode__(self):
        return self.name
    class Meta:
        # ordering = ("Name",)
        verbose_name_plural = 'Modules'


class CasestudiesCsType(models.Model):
    """
    LISTA DEI Cs Type CASE STUDIES
    """
    # group = models.ForeignKey(GroupProfile, related_name='group_collections')
    # resources = models.ManyToManyField(ResourceBase, related_name='resource_collections')
    name = models.CharField(max_length=128, unique=True)
    slug = models.SlugField(max_length=128, unique=True)

    def __unicode__(self):
        return self.name
    class Meta:
        # ordering = ("Name",)
        verbose_name_plural = 'Types'
    
class CasestudiesToken(models.Model):

    # group = models.ForeignKey(GroupProfile, related_name='group_collections')
    # resources = models.ManyToManyField(ResourceBase, related_name='resource_collections')
    label = models.CharField(max_length=128, unique=True)
    token = models.SlugField(max_length=128, unique=True)
    schema = models.CharField(max_length=500, unique=False)
    is_enabled = models.BooleanField(
        default=False,
        help_text="Enabling this theme will disable the current enabled toke (if any)")

    def __unicode__(self):
        return self.label
    
    class Meta:
        # ordering = ("Name",)
        verbose_name_plural = 'Token'


# Disable other themes if one theme is enabled.
@receiver(post_save, sender=CasestudiesToken)
def disable_other(sender, instance, **kwargs):
    if instance.is_enabled:
        CasestudiesToken.objects.exclude(pk=instance.pk).update(is_enabled=False)



"""   
class CasestudiesList(models.Model):

    # group = models.ForeignKey(GroupProfile, related_name='group_collections')
    # resources = models.ManyToManyField(ResourceBase, related_name='resource_collections')

    casestudy_api_id = models.IntegerField(verbose_name="API Case Study ID",  null=False, serialize=False, editable=True )   # cs id del WS tools4msp 
    casestudy_pdm_id = models.AutoField(verbose_name="Porto di Mare Case Study ID", serialize=False, auto_created=True, primary_key=True)   # cs id del DB locale PORTO DI MARE 
    # user_id = models.IntegerField(verbose_name="User ID", null=False)     # user id del DB locale PORTO DI MARE
    user = models.ForeignKey(get_user_model(), on_delete=models.CASCADE, null=True)
    # associare gruppo non utente
    
    def __unicode__(self):
        return self.casestudy_api_id
    
    class Meta:
        ordering = ("casestudy_api_id",)
        verbose_name_plural = 'List'
"""

# class CasestudiesListSerializer(serializers.Serializer):        
#         class Meta:
#             model = CasestudiesList
#             fields = ('casestudy_api_id')


