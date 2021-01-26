# -*- coding: utf-8 -*-
#########################################################################
#
# Copyright (C) 2018 OSGeo
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.
#
#########################################################################
from django.apps import AppConfig as BaseAppConfig

from django import forms
from django.db import models
from django.db.models import Q, signals
from django.utils.translation import ugettext_lazy as _

from autocomplete_light.widgets import ChoiceWidget

def run_setup_hooks(*args, **kwargs):
    from django.conf import settings
    from .celeryapp import app as celeryapp
    if celeryapp not in settings.INSTALLED_APPS:
        settings.INSTALLED_APPS += (celeryapp, )


class AppConfig(BaseAppConfig):

    name = "porto_di_mare"
    label = "porto_di_mare"

    def _get_logger(self):
        import logging
        return logging.getLogger(self.__class__.__module__)

    def patch_topic_category(self, cls):
        from base_ext.models import MainCategory

        self._get_logger().info("Patching Resource Base")
        maincategory_help_text = _(
            'a Main Category will be added by Admin before publication.')
        maincategory = models.ForeignKey(
            MainCategory,
            null=True,
            blank=True,
            limit_choices_to=Q(
                 is_choice=True),
            help_text=maincategory_help_text)
        cls.add_to_class('main_category', maincategory)

    def patch_domain_area(self, cls):
        from base_ext.models import DomainArea

        self._get_logger().info("Patching Resource Base -> Domain Area")
        domainarea_help_text = _(
            'a Domain Area will be added by Admin before publication.')
        domainarea = models.ManyToManyField(
            DomainArea,
            related_name='resourcebase_domainarea',
            help_text=domainarea_help_text,
            blank=True)
        cls.add_to_class('domain_area', domainarea)

        def domain_area_identifier_list(self):
            return [domain_area.identifier for domain_area in self.domain_area.all()]
        cls.add_to_class('domain_area_identifier_list', domain_area_identifier_list)
        

    def patch_data_portal(self, rb):
        from base_ext.models import DataPortal

        self._get_logger().info("Patching Resource Base -> Data Portal")
        dataportal_help_text = _(
            'a Data Portal will be added by Admin before publication.')
        dataportal = models.ForeignKey(
            DataPortal,
            null=True,
            blank=True,
            limit_choices_to=Q(
                 is_choice=True),
            help_text=dataportal_help_text)
        rb.add_to_class('data_portal', dataportal)

    def patch_data_accessibility(self, cls):
      
        self._get_logger().info("Patching Resource Base -> Data Accessibility")
        dataaccessibility_help_text = _(
            'a Data Accessibility will be added by Admin before publication.')
        dataaccessibility = models.TextField(
            _('data accessibility'),
            default='',
            null=True,
            blank=True,
            help_text=dataaccessibility_help_text)
        cls.add_to_class('data_accessibility', dataaccessibility)
    
    def patch_validation_level(self, cls):
        from base_ext.models import ValidationLevel

        self._get_logger().info("Patching Resource Base -> Validation Level")
        validationlevel_help_text = _(
            'a Validation Level will be added by Admin before publication.')
        validationlevel = models.ForeignKey(
            ValidationLevel,
            null=True,
            blank=True,
            limit_choices_to=Q(
                 is_choice=True),
            help_text=validationlevel_help_text)
        cls.add_to_class('validation_level', validationlevel)


    def patch_starred(self, cls):
      
        self._get_logger().info("Patching Resource Base -> Starred")
        starred_help_text = _(
            'a Starred will be added by Admin before publication.')
        starred = models.BooleanField(
            _('starred'),
            default=False,
            help_text=starred_help_text)
        cls.add_to_class('starred', starred)


    def ready(self):
        super(AppConfig, self).ready()
        run_setup_hooks()

        from geonode.base.models import TopicCategory
        self.patch_topic_category(TopicCategory)
        
        from geonode.base.models import ResourceBase
        self.patch_domain_area(ResourceBase)
        self.patch_data_portal(ResourceBase)
        self.patch_data_accessibility(ResourceBase)
        self.patch_validation_level(ResourceBase)
        self.patch_starred(ResourceBase)
