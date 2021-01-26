# -*- coding: utf-8 -*-
#########################################################################
#
# Copyright (C) 2017 OSGeo
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

from django.conf.urls import url, include
from django.views.generic import TemplateView

from geonode.urls import urlpatterns

from tastypie.api import Api
from api_ext import api_ext as resources
from api_ext import resources as resourcebase_resources

from . import views

api_ext = Api(api_name='ext')

api_ext.register(resources.GroupCategoryResource())
api_ext.register(resources.GroupResource())
api_ext.register(resources.OwnersResource())
api_ext.register(resources.ProfileResource())
api_ext.register(resources.RegionResource())
api_ext.register(resources.TagResource())
api_ext.register(resources.ThesaurusKeywordResource())
api_ext.register(resources.MainCategoryResource())
api_ext.register(resources.TopicCategoryResource())
api_ext.register(resources.DomainAreaResource())
api_ext.register(resources.DataPortalResource())
api_ext.register(resources.ValidationLevelResource())
api_ext.register(resourcebase_resources.DocumentResource())
api_ext.register(resourcebase_resources.FeaturedResourceBaseResource())
api_ext.register(resourcebase_resources.LayerResource())
api_ext.register(resourcebase_resources.MapResource())
api_ext.register(resourcebase_resources.ResourceBaseResource())

urlpatterns += [
    ## include your urls here
    url(r'^api/', include(api_ext.urls)),
    url(r'^casestudies/', include('casestudies.urls')),
    url(r'^api_casestudies/', include('api_casestudies.urls')),
    url(r'^layers_ext/', include('layers_ext.urls')),
    url(r'^maps_ext/', include('maps_ext.urls')),
    url(r'^documents_ext/', include('documents_ext.urls')),
    url(r'^geodatabuilder/', include('geodatabuilder.urls')),
    url(r'^tools_r/', include('tools_r.urls')),

    # ident
    url(r'^ident.json$',
        views.ident_json,
        name='ident_json'),
]

urlpatterns = [
   url(r'^/?$',
       TemplateView.as_view(template_name='site_index.html'),
       name='home'),
 ] + urlpatterns