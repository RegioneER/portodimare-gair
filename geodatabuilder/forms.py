# -*- coding: utf-8 -*-
#########################################################################
#
# Copyright (C) 2016 OSGeo
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

import json
import os
import re
from autocomplete_light.registry import autodiscover

from django import forms
from django.utils.translation import ugettext as _
from django.contrib.contenttypes.models import ContentType
from django.conf import settings
from django.forms import HiddenInput
from modeltranslation.forms import TranslationModelForm

from autocomplete_light.widgets import ChoiceWidget

from geonode.people.models import Profile

from .models import (
    GeoDataBuilder,
)

autodiscover()  # flake8: noqa


class GeoDataBuilderForm(TranslationModelForm):

    """
    owner = forms.ModelChoiceField(
        empty_label="Owner",
        label=_("Owner"),
        required=True,
        queryset=Profile.objects.exclude(
            username='AnonymousUser'),
        widget=ChoiceWidget('ProfileAutocomplete'))
    """

    label = forms.CharField(label=_('Name'), required=True, 
                widget= forms.TextInput(
                    attrs={ 'class':'form-control'}))

    expression = forms.CharField(2000, label=_('Expression (ID)'), 
                widget=forms.Textarea(
                    attrs={ 'id':'expression_id',
                            'readonly':'readonly',
                            'class' : ''
                        }), 
                    required=True)
    
    desc_expression = forms.CharField(2000, label=_('Expression'), 
                widget=forms.Textarea(
                    attrs={ 'id':'expression_text', 
                            'class' : 'form-control'
                        }), 
                    required=True)
        
    expression_id_string = forms.CharField(2000, label=_('Expression String (ID)'), 
                widget=forms.Textarea(
                    attrs={ 'id':'expression_id_string',
                            'readonly':'readonly',
                            'class' : ''
                        }), 
                    required=True)

    casestudy_api_id = forms.IntegerField(
                widget=forms.Select(
                    attrs={ 'id':'casestudy',
                            'class':'form-control',
                            'required': 'required'
                        }), 
                    required=True)

    def __init__(self, *args, **kwargs):
        super(GeoDataBuilderForm, self).__init__(*args, **kwargs)
        

    class Meta:
        model = GeoDataBuilder
        fields = '__all__'
        exclude = ('owner','created','updated','status',)
