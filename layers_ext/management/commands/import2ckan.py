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

from ckanapi import RemoteCKAN
import time, os, sys, traceback, urllib2, xlsxwriter, wget, requests, zipfile, random, string
from urlparse import urlparse

from django.conf import settings
from django.core.management.base import BaseCommand
from django.core.management import call_command

from geonode.base.enumerations import ALL_LANGUAGES, \
    HIERARCHY_LEVELS, UPDATE_FREQUENCIES, \
    DEFAULT_SUPPLEMENTAL_INFORMATION, LINK_TYPES

import logging
logger = logging.getLogger("geonode.documents.views")

def randomString(stringLength=10):
    """Generate a random string of fixed length """
    letters = string.ascii_lowercase
    return ''.join(random.choice(letters) for i in range(stringLength))

def login(urlckan, username, password):
    '''
    Login to CKAN.

    Returns a ``requests.Session`` instance with the CKAN
    session cookie.
    '''
    s = requests.Session()
    data = {'login': username, 'password': password}
    url = urlckan + '/login_generic'
    r = s.post(url, data=data)
   
    if 'field-login' in r.text:
        # Response still contains login form
        raise RuntimeError('Login failed.')
    return s

def GarbageCollector(d):
    l=[]
    for name in d:
        if not name.startswith('_'):
            l.append(name)
    return l

def download_resource_data(urlckan, session, url, directory, nome_file, extension):
    
    parsed_uri = urlparse(url)
    result = '{uri.scheme}://{uri.netloc}'.format(uri=parsed_uri)
    if (result == urlckan):
        myfile = session.get(url,allow_redirects=True).content
    else:
        myfile = requests.get(url,verify=False).content
  
    open(directory + "/%s%s" % (nome_file,extension), "wb").write(myfile)
    return directory + "/%s%s" % (nome_file,extension)

def importData(filename, rec, directory, overwrite, regions, permission, keywords, name):
    
    if not name:
        name = (rec["name"][:24]+'_'+randomString(5)) if len(rec["name"]) > 30 else rec["name"]
    supplemental_information = rec["additional_informations"]
    if supplemental_information is None or supplemental_information == '':
        supplemental_information = DEFAULT_SUPPLEMENTAL_INFORMATION
    
    tags = []
    if keywords:
        for tag in rec["tags"]:
            tags.append(tag["name"])

    temporal_extent_start = None 
    if rec.has_key("temporal_extent"):
        temporal_extent_start = rec["temporal_extent"]

    temporal_extent_end = None 
    if rec.has_key("temporal_extent_end"):
        temporal_extent_end = rec["temporal_extent_end"]
   
    call_command('importlayers_ext', filename, overwrite=overwrite, \
        title=rec["title"], \
        name=name, \
        category=rec["sub_category"], \
        abstract=rec["notes"].replace("'", ""), \
        supplemental_information=supplemental_information, \
        license=rec["license_title"], \
        data_portal=rec["data_portal"], \
        validation_level=rec["validation_level"], \
        data_accessibility=rec["data_accessibility"], \
        spatial_representation_type=rec["spatial_representation"], \
        temporal_extent_start=temporal_extent_start, \
        temporal_extent_end=temporal_extent_end, \
        keywords=','.join(tags), \
        regions=regions,\
        #data=rec["metadata_modified"], \
        user=rec["owner"].replace(" ", "-").replace(",", "-"), \
        domain_area=rec["domain_area"], \
        directory=directory, \
        groups=settings.GROUPS_PDM[rec["pdm_partner"]], \
        permission=permission)


def dataCheck(filezip):
    zippo=zipfile.ZipFile(filezip)
    fl = zippo.infolist()
    nomi_file = []
    for f in fl:
        if "." in f.name:
            if f.name not in nomi_file:
                nomi_file.append(f.name)
    return nomi_file 

def check_layer(namelayers, name):
    if namelayers:
        layers = namelayers.split(',')
        for l in layers:
            if l == name:
                return True
        return False
    else:
        return True

class Command(BaseCommand):
    help = ("PDM: Export layer.....")

    def add_arguments(self, parser):
      
        # Named (optional) arguments
        parser.add_argument(
            '-o',
            '--overwrite',
            dest='overwrite',
            default=False,
            action="store_true",
            help="Overwrite existing layers if discovered (defaults False)")

        parser.add_argument(
            '-d',
            '--directory',
            dest="directory",
            default='/var/log/import2ckan',
            help="import2ckan directory")

        parser.add_argument(
            '-u',
            '--urlckan',
            dest="urlckan",
            default='http://catalogue.msp-supreme.eu',
            help="url ckan")

        parser.add_argument(
            '-us',
            '--user',
            dest="user",
            default='',
            help="user login ckan")
        
        parser.add_argument(
            '-pw',
            '--password',
            dest="password",
            default='',
            help="password login ckan")

        parser.add_argument(
            '-ua',
            '--ua',
            dest="ua",
            default='ckanapiexample/1.0 (+http://catalogue.msp-supreme.eu)',
            help="ua")
        
        parser.add_argument(
            '-ak',
            '--ak',
            dest="ak",
            default='f5f9f97e-c29c-4069-8f54-7d951d1f4755',
            help="ak")
        
        parser.add_argument(
            '-rows',
            '--rows',
            dest="rows",
            default='1000000000000000000',
            help="rows")
        
        parser.add_argument(
            '-org',
            '--organization',
            dest="organization",
            default='portodimare',
            help="organization")
        
        parser.add_argument(
            '-l',
            '--log',
            dest="log",
            default='export.log',
            help="file log")
        
        parser.add_argument(
            '-nl',
            '--namelayers',
            dest="namelayers",
            default=None,
            help="The name layers, separated by comma, for the imported"
                  " layer(s)")
        
        parser.add_argument(
            '-r',
            '--regions',
            dest='regions',
            default="EUR",
            help=("The default regions, separated by comma, for the imported"
                  " layer(s). Will be the same for all imported layers if"
                  " multiple imports are done in one command"))
        
        parser.add_argument(
            '-pm',
            '--permission',
            dest='permission',
            type=str,
            default='o',
            help='Permissions to be assigned. '
                 'Allowed values are: read (r), write (w), download (d) and owner (o).'
        )

        parser.add_argument(
            '-k',
            '--keywords',
            dest='keywords',
            default=False,
            help="Insert keywords (defaults False)")
        
        parser.add_argument(
            '-f',
            '--datafile',
            dest='datafile',
            default=False,
            help="data file layers for import (Supported extensions are: .shp, .tif, .tar, .tar.gz, and .zip (of a shapefile))")

        parser.add_argument(
            '-sn',
            '--sname',
            dest="sname",
            default=None,
            help="The specific name layer")


    def handle(self, *args, **options):

        overwrite = options.get('overwrite')
        directory = options.get('directory', None)
        urlckan = options.get('urlckan', None)
        ua = options.get('ua', None)
        ak = options.get('ak', None)
        user = options.get('user', None)
        password = options.get('password', None)
        log = options.get('log', None)
        rows = int(options.get('rows', None))
        organization = options.get('organization', None)
        namelayers = options.get('namelayers', None)
        regions = options.get('regions', None)
        permission = options.get('permission', None)
        keywords = options.get('keywords', None)
        datafile = options.get('datafile', None)
        sname = options.get('sname', None)

        if not os.path.exists(directory):
            os.makedirs(directory)
            os.makedirs(directory + '/downloads_temp')

        f = open(directory + '/' + log,"w")

        session = login(urlckan, user, password)
       
        catalogo = RemoteCKAN(urlckan, apikey=ak, user_agent=ua)
        org = catalogo.action.organization_list()
        res = catalogo.action.package_search(rows=rows, include_private=True)
        
        try:
            i=0
            for r in res["results"]:
                if (not check_layer(namelayers,r["name"])):
                    continue
                try:
                    if r.has_key("organization") and r.has_key("import_preferences"):    
                        if (r["organization"]["name"] == organization and r["import_preferences"] == 'comfirmed' ):
                            itemid=r["id"]
                            name=r["name"]
                            title=r["title"]
                            risorsa=r["resources"]
                            for ris in risorsa:
                                if ris["mspkc_resource_type"] == "GeospatialDataset":
                                    i+=1
                                    link_risorsa = ris["url"]
                                    urlsplit = ris["url"].split("/")
                                    nomefile = urlsplit[len(urlsplit)-1]
                                    base_name, extension = os.path.splitext(nomefile)
                                    f.write(str(i)+'|'+str(itemid)+'|'+str(name)+'|'+str(title)+'|'+str(link_risorsa)+'|'+nomefile+'\n')
                                    if (not datafile) or (not namelayers):
                                        filename = download_resource_data(urlckan, session, ris["url"], directory + '/downloads_temp', str(i)+'_'+str(itemid), extension)
                                    else:
                                        filename = datafile
                                    importData(filename, r, directory, overwrite, regions, permission, keywords, sname)
                                 
                                    #if (i == 1):
                                    #    break
                                 
                except:
                    tb = sys.exc_info()[2]
                    tbinfo = traceback.format_tb(tb)[0]
                    pymsg = "Generic Error Info:" + str(sys.exc_info()[1])
                    f.write(str(r["id"])+'|'+r["title"]+'|'+str(pymsg)+'|\n')
            
            f.close()   

        except:
            tb = sys.exc_info()[2]
            tbinfo = traceback.format_tb(tb)[0]
            pymsg = "Global Error Info:" + str(sys.exc_info()[1])
            f.write(''+'|'+''+'|'+str(pymsg)+'|\n')
            f.close()

        finally:
            f.close()
            lista=GarbageCollector(dir())
            for l in lista:
          #      print 'cancello %s' %(l)
                del locals()[l]
            del lista        
