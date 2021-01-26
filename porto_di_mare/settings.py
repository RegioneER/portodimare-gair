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

# Django settings for the GeoNode project.
import ast
import os
from urlparse import urlparse, urlunparse
# Load more settings from a file called local_settings.py if it exists
try:
    from porto_di_mare.local_settings import *
#    from geonode.local_settings import *
except ImportError:
    from porto_di_mare.settings import *

#
# General Django development settings
#
PROJECT_NAME = 'porto_di_mare'

#
# Extension APP
#
BASE_EXT_NAME = 'base_ext'
CASESTUDIES_NAME = 'casestudies'
APICASESTUDIES_NAME = 'api_casestudies'
REST_FRAMEWORK_NAME = 'rest_framework'
LAYERS_EXT_NAME = 'layers_ext'
MAPS_EXT_NAME = 'maps_ext'
DOCUMENTS_EXT_NAME = 'documents_ext'
CLIENT_EXT_NAME = 'client_ext'
GEODATABUILDER_NAME = 'geodatabuilder'
TOOLS_R_NAME = 'tools_r'
DEFAULT_CASESTUDY_TYPE_ID = 2
# indica l'id di default dei TYPE dei Case Study

# https://zoejoyuliao.medium.com/the-problem-you-may-face-when-you-upload-a-big-file-to-a-nginx-django-application-413-request-4ae9b50874a5
# 1048576 * 400 => 400M è impostato in playbook.yml - nginx_client_max_body_size: "400M"
DATA_UPLOAD_MAX_MEMORY_SIZE = 419430400

# add trailing slash to site url. geoserver url will be relative to this
if not SITEURL.endswith('/'):
    SITEURL = '{}/'.format(SITEURL)

SITENAME = os.getenv("SITENAME", 'porto_di_mare')

# Defines the directory that contains the settings file as the LOCAL_ROOT
# It is used for relative settings elsewhere.
LOCAL_ROOT = os.path.abspath(os.path.dirname(__file__))

WSGI_APPLICATION = "{}.wsgi.application".format(PROJECT_NAME)

# Language code for this installation. All choices can be found here:
# http://www.i18nguy.com/unicode/language-identifiers.html
LANGUAGE_CODE = os.getenv('LANGUAGE_CODE', "en")

if PROJECT_NAME not in INSTALLED_APPS:
    INSTALLED_APPS += (PROJECT_NAME,)

if BASE_EXT_NAME not in INSTALLED_APPS:
    INSTALLED_APPS += (BASE_EXT_NAME,)

if CASESTUDIES_NAME not in INSTALLED_APPS:
    INSTALLED_APPS += (CASESTUDIES_NAME,)

if APICASESTUDIES_NAME not in INSTALLED_APPS:
    INSTALLED_APPS += (APICASESTUDIES_NAME,)

if REST_FRAMEWORK_NAME not in INSTALLED_APPS:
    INSTALLED_APPS += (REST_FRAMEWORK_NAME,)

if LAYERS_EXT_NAME not in INSTALLED_APPS:
    INSTALLED_APPS += (LAYERS_EXT_NAME,)

if MAPS_EXT_NAME not in INSTALLED_APPS:
    INSTALLED_APPS += (MAPS_EXT_NAME,)

if DOCUMENTS_EXT_NAME not in INSTALLED_APPS:
    INSTALLED_APPS += (DOCUMENTS_EXT_NAME,)

if CLIENT_EXT_NAME not in INSTALLED_APPS:
    INSTALLED_APPS += (CLIENT_EXT_NAME,)

if GEODATABUILDER_NAME not in INSTALLED_APPS:
    INSTALLED_APPS += (GEODATABUILDER_NAME,)

if TOOLS_R_NAME not in INSTALLED_APPS:
    INSTALLED_APPS += (TOOLS_R_NAME,)

# Location of url mappings
ROOT_URLCONF = os.getenv('ROOT_URLCONF', '{}.urls'.format(PROJECT_NAME))

# Additional directories which hold static files
STATICFILES_DIRS.append(
    os.path.join(LOCAL_ROOT, "static"),
)

# Additional filter
SEARCH_FILTERS = {
    'TEXT_ENABLED': True,
    'TYPE_ENABLED': True,
    'CATEGORIES_ENABLED': True,
    'OWNERS_ENABLED': True,
    'KEYWORDS_ENABLED': True,
    'H_KEYWORDS_ENABLED': True,
    'T_KEYWORDS_ENABLED': True,
    'DATE_ENABLED': True,
    'REGION_ENABLED': True,
    'EXTENT_ENABLED': True,
    'GROUPS_ENABLED': True,
    'GROUP_CATEGORIES_ENABLED': True,
    'DATA_PORTAL_ENABLED': True,
    'DOMAIN_AREA_ENABLED': True,
    'VALIDATION_LEVEL_ENABLED': True,
    'STARRED': True
    }

# Location of locale files
LOCALE_PATHS = (
    os.path.join(LOCAL_ROOT, 'locale'),
    ) + LOCALE_PATHS

TEMPLATES[0]['DIRS'].insert(0, os.path.join(LOCAL_ROOT, "templates"))
loaders = TEMPLATES[0]['OPTIONS'].get('loaders') or ['django.template.loaders.filesystem.Loader','django.template.loaders.app_directories.Loader']
# loaders.insert(0, 'apptemplates.Loader')
TEMPLATES[0]['OPTIONS']['loaders'] = loaders
TEMPLATES[0].pop('APP_DIRS', None)

UNOCONV_ENABLE = strtobool(os.getenv('UNOCONV_ENABLE', 'True'))

if UNOCONV_ENABLE:
    UNOCONV_EXECUTABLE = os.getenv('UNOCONV_EXECUTABLE', '/usr/bin/unoconv')
    UNOCONV_TIMEOUT = os.getenv('UNOCONV_TIMEOUT', 30)  # seconds

REST_FRAMEWORK = {
    # Use Django's standard `django.contrib.auth` permissions,
    # or allow read-only access for unauthenticated users.
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.AllowAny',
    ]
}