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
    url(r'^(?P<mapid>[^/]+)$', views.map_detail, name='map_detail'),
    url(r'^(?P<mapid>[^/]+)/metadata$', views.map_metadata, name='map_metadata'),
    url(r'^(?P<mapid>[^/]+)/metadata_advanced$', views.map_metadata_advanced, name='map_metadata_advanced'),
    url(r'^(?P<mapid>[^/]+)/remove$', views.map_remove, name='map_remove'),   
]