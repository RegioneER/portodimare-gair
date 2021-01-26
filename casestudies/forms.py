from geonode.base.fields import MultiThesauriField
from geonode.base.widgets import MultiThesauriWidget

from autocomplete_light.widgets import ChoiceWidget
from autocomplete_light.contrib.taggit_field import TaggitField, TaggitWidget

from django import forms
from django.conf import settings
from django.core import validators
from django.forms import models
from django.forms import ModelForm
from django.forms.fields import ChoiceField
from django.forms.utils import flatatt
from django.utils.html import format_html
from django.utils.safestring import mark_safe
from django.utils.translation import ugettext as _
from django.db.models import Q

from django.utils.encoding import (
    force_text,
)

from bootstrap3_datetime.widgets import DateTimePicker
from modeltranslation.forms import TranslationModelForm

from geonode.base.models import HierarchicalKeyword, TopicCategory, Region, License #, CuratedThumbnail
from geonode.people.models import Profile
from geonode.base.enumerations import ALL_LANGUAGES
from django.contrib.auth.models import Group
from django.contrib.auth import get_user_model

#from casestudies.models import CasestudiesList


# from itertools import groupby
# from operator import attrgetter

"""
class CasestudiesListForm(forms.ModelForm):

    class Meta:
        model = CasestudiesList
        fields = [
            'casestudy_api_id',
        ]
"""