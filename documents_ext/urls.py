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
    url(r'upload/?$',
        views.DocumentUploadView.as_view(), name='document_upload'),
    url(r'^(?P<docid>\d+)/?$',
        views.document_detail, name='document_detail'),
    url(r'^(?P<docid>\d+)/metadata$',
        views.document_metadata, name='document_metadata'),
    url(r'^(?P<docid>\d+)/metadata_advanced$', views.document_metadata_advanced,
        name='document_metadata_advanced'),
    url(r'^(?P<docid>\d+)/remove$',
        views.document_remove, name="document_remove"),
]