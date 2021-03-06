# -*- coding: utf-8 -*-
# ##############################################################################
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
# ##############################################################################

from django.conf.urls import url
from django.views.generic import TemplateView

from . import views

urlpatterns = [
    url(r'^(?P<layername>[^/]*)$', views.layer_detail, name="layer_detail"),
    url(r'^(?P<layername>[^/]*)/metadata$',
        views.layer_metadata, name="layer_metadata"),
    url(r'^(?P<layername>[^/]*)/metadata_advanced$',
        views.layer_metadata_advanced, name="layer_metadata_advanced"),
    url(r'^get_layer_by_id/(?P<id>[^/]*)/$',
        views.get_layer_by_id, name="get_layer_by_id"),
    url(r'^(?P<layername>[^/]*)/thumbnail$',
        views.layer_thumbnail, name='layer_thumbnail'),
    url(r'^(?P<layername>[^/]*)/remove$',
        views.layer_remove, name="layer_remove"),
]