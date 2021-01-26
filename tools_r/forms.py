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
    ToolsR_1_8,
    ToolsR_1_11,
    ToolsR_1_12,
)

autodiscover()  # flake8: noqa


class ToolsR_1_8Form(TranslationModelForm):

    type = forms.IntegerField(
        widget = forms.HiddenInput(
            attrs={  
                "id" : "type",
            }
        ),
        initial= settings.DEFAULT_CASESTUDY_TYPE_ID  # "Default"
    )

    label = forms.CharField(label=_('Label'), required=True, 
                widget= forms.TextInput(
                    attrs={ 'class':'form-control'}))

    input_layers = forms.CharField(2000, label=_('Input Layers (ID)'), 
                widget=forms.Textarea(
                    attrs={ 'id':'input_layers_id',
                            'readonly':'readonly',
                            'class' : ''
                        }), 
                    required=True)
    
    input_criteria = forms.CharField(2000, label=_('Input Criteria'))
    
    public = forms.BooleanField(required=False)
    
    def __init__(self, *args, **kwargs):
        super(ToolsR_1_8Form, self).__init__(*args, **kwargs)
        

    class Meta:
        model = ToolsR_1_8
        fields = '__all__'
        exclude = ('owner','created','updated','status','output_files')


class ToolsR_1_11Form(TranslationModelForm):

    type = forms.IntegerField(
        widget = forms.HiddenInput(
            attrs={  
                "id" : "type"
            }
        ),
        initial= settings.DEFAULT_CASESTUDY_TYPE_ID  # "Default"
    )


    label = forms.CharField(label=_('Label'), required=True, 
                widget= forms.TextInput(
                    attrs={ 'class':'form-control'}))

    input_layers = forms.CharField(2000, label=_('Input Layers (ID)'), 
                widget=forms.Textarea(
                    attrs={ 'id':'input_layers_id',
                            'readonly':'readonly',
                            'class' : ''
                        }), 
                    required=True)
    
    input_criteria = forms.CharField(2000, label=_('Input Criteria'))

    pairwise_matrix = forms.CharField(2000, label=_('Pairwise matrix'), 
                widget=forms.Textarea(
                    attrs={ 'id':'pairwise_matrix_id',
                            'readonly':'readonly',
                            'class' : ''
                        }), 
                    required=True)
    
    fishing_gear = forms.CharField(9000, label=_('Fishing gear'), 
                widget=forms.Textarea(
                    attrs={ 'id':'fishing_gear_id',
                            'readonly':'readonly',
                            'class' : ''
                        }), 
                    required=True)

    public = forms.BooleanField(required=False)
    
    def __init__(self, *args, **kwargs):
        super(ToolsR_1_11Form, self).__init__(*args, **kwargs)
        

    class Meta:
        model = ToolsR_1_11
        fields = '__all__'
        exclude = ('owner','created','updated','status','output_files')


class ToolsR_1_12Form(TranslationModelForm):

    type = forms.IntegerField(
        widget = forms.HiddenInput(
            attrs={  
                "id" : "type"
            }
        ),
        initial= settings.DEFAULT_CASESTUDY_TYPE_ID  # "Default"
    )


    label = forms.CharField(label=_('Label'), required=True, 
                widget= forms.TextInput(
                    attrs={ 'class':'form-control'}))

    input_layers = forms.CharField(2000, label=_('Input Layers (ID)'), 
                widget=forms.Textarea(
                    attrs={ 'id':'input_layers_id',
                            'readonly':'readonly',
                            'class' : ''
                        }), 
                    required=True)
    
    input_criteria = forms.CharField(2000, label=_('Input Criteria'))

    pairwise_matrix_ps = forms.CharField(2000, label=_('Pairwise matrix ps'), 
                widget=forms.Textarea(
                    attrs={ 'id':'pairwise_matrix_ps_id',
                            'readonly':'readonly',
                            'class' : ''
                        }), 
                    required=True)
    
    pairwise_matrix_tr = forms.CharField(2000, label=_('Pairwise matrix tr'), 
                widget=forms.Textarea(
                    attrs={ 'id':'pairwise_matrix_tr_id',
                            'readonly':'readonly',
                            'class' : ''
                        }), 
                    required=True)
    
    fishing_gear_ps = forms.CharField(9000, label=_('Fishing gear ps'), 
                widget=forms.Textarea(
                    attrs={ 'id':'fishing_gear_ps_id',
                            'readonly':'readonly',
                            'class' : ''
                        }), 
                    required=True)
    
    fishing_gear_tr1224 = forms.CharField(9000, label=_('Fishing gear tr1224'), 
                widget=forms.Textarea(
                    attrs={ 'id':'fishing_gear_tr1224_id',
                            'readonly':'readonly',
                            'class' : ''
                        }), 
                    required=True)
    
    fishing_gear_tr2440 = forms.CharField(9000, label=_('Fishing gear tr2440'), 
                widget=forms.Textarea(
                    attrs={ 'id':'fishing_gear_tr2440_id',
                            'readonly':'readonly',
                            'class' : ''
                        }), 
                    required=True)

    public = forms.BooleanField(required=False)
    
    def __init__(self, *args, **kwargs):
        super(ToolsR_1_12Form, self).__init__(*args, **kwargs)
        

    class Meta:
        model = ToolsR_1_12
        fields = '__all__'
        exclude = ('owner','created','updated','status','output_files')

