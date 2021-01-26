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

from django.utils import timezone
from django.core.management.base import BaseCommand
from django.core.files.storage import default_storage as storage
from django.utils.translation import ugettext as _

from django.conf import settings

from geonode.utils import (resolve_object,get_dir_time_suffix,zip_dir)
from geonode.layers.models import Layer, LayerFile
from geonode.people.utils import get_valid_user

from tools_r.models import ToolsR_1_12

from osgeo import gdal

import os, traceback, datetime, tempfile, shutil, re, string, subprocess, sys, random, string, socket, csv

import logging
logger = logging.getLogger("geonode.documents.views")

gdal
def getFilesToId(resourceid, target_folder):
    layers = Layer.objects.filter(id=resourceid)
    if layers:
        instance = layers[0]
    
    if isinstance(instance, Layer):
        try:
            upload_session = instance.get_upload_session()
            layer_files = [item for idx, item in enumerate(LayerFile.objects.filter(upload_session=upload_session))]
        
            for l in layer_files:
                if storage.exists(l.file):
                    geonode_layer_path = storage.path(l.file)
                    base_filename, original_ext = os.path.splitext(geonode_layer_path)
                    shutil.copy2(geonode_layer_path, target_folder)
            
            return instance
                
        except NotImplementedError:
            traceback.print_exc()
            tb = traceback.format_exc()
            logger.debug(tb)
            return "file not found"
        
    else:
        return "layer not found"

def getNumbers(str): 
    array = re.findall(r'[0-9]+', str) 
    return array 

def randomString(stringLength=6):
    """Generate a random string of fixed length """
    letters = string.ascii_lowercase
    return ''.join(random.choice(letters) for i in range(stringLength))

class Command(BaseCommand):
    help = ("PDM: Run Tool R 1.8 ....")

    def add_arguments(self, parser):
      
        parser.add_argument(
            '-i',
            '--id_tool',
            dest="id_tool",
            default=None,
            help="id tool")

        parser.add_argument(
            '-n',
            '--name',
            dest="name",
            default='MSF',
            help="app domain")

        parser.add_argument(
            '-c',
            '--criteria',
            dest="criteria",
            default=None,
            help="Criteria with [id;name_layer] (name_layer if geotiff) -> ex: '101,96;no_take,97;coast_dist,95;marine_traffic,94;trawl_fleet,93;'")

        parser.add_argument(
            '-d',
            '--directory',
            dest="directory",
            default="/mnt/volumes/statics/static/script_r/1.12/",
            help="Directory R Server with script files")
        
        parser.add_argument(
            '-o',
            '--output',
            dest="output",
            default="/mnt/volumes/statics/uploaded/tools_r/1.12/",
            help="Directory output files")
        
        parser.add_argument(
            '-s',
            '--strtoolr',
            dest="strtoolr",
            default=randomString(),
            help="Unique string Tool R (output directory)")

    def handle(self, *args, **options):

        id_tool = options.get('id_tool', None)

        name = options.get('name', None)
        
        criteria = options.get('criteria', None)
        
        directory = options.get('directory', None)
        strtoolr = options.get('strtoolr', None)
        output = options.get('output', None)

        # verifica se esiste la directory utilizzata per eseguire gli script R
        if os.path.exists(directory):

            # crea la directory temporanea e di output
            dir_temp = tempfile.mkdtemp()[1:]+'/'
            if not os.path.exists(directory+dir_temp+'output/'):
                os.makedirs(directory+dir_temp+'output/')
            
            # crea la directory per l'output esposta su web
            dir_output = output+strtoolr+'/'
            if not os.path.exists(dir_output):
                os.makedirs(dir_output)
                if os.path.isfile(directory+'pairwise_matrix_PS.csv'):
                    shutil.copy2(directory+'pairwise_matrix_PS.csv', dir_output)
                if os.path.isfile(directory+'pairwise_matrix_TR.csv'):
                    shutil.copy2(directory+'pairwise_matrix_TR.csv', dir_output)
                if os.path.isfile(directory+'Fishing_Gear_PS.csv'):
                    shutil.copy2(directory+'Fishing_Gear_PS.csv', dir_output)
                if os.path.isfile(directory+'Fishing_Gear_TR1224.csv'):
                    shutil.copy2(directory+'Fishing_Gear_TR1224.csv', dir_output)
                if os.path.isfile(directory+'Fishing_Gear_TR2440.csv'):
                    shutil.copy2(directory+'Fishing_Gear_TR2440.csv', dir_output)
         
            # creo il csv e carico i layers nella cartella temporanea
            replacements = {}
            str_input = ""
            arr_crit = []
            extent = ""
            coastLine = ""
            no_take_ps = ""
            no_take_tr = ""
            fpc_ssf = ""
            geotiff = ""
            logger.info(directory+dir_temp)
            for c in criteria.split(','):
                temp = c.split(';')
                layer = getFilesToId(int(temp[0]), directory+dir_temp)
                if (len(temp)>1):
                    if (temp[1] == "no_take_ps"):
                        no_take_ps = "1.12/"+dir_temp+layer.name+".tif"
                        extent = str(layer.bbox_x0)+" "+str(layer.bbox_x1)+" "+str(layer.bbox_y0)+" "+str(layer.bbox_y1)
                    elif (temp[1] == "no_take_tr"):
                        no_take_tr = "1.12/"+dir_temp+layer.name+".tif"
                    elif (temp[1]) == "fpc_ssf":
                        fpc_ssf = "1.12/"+dir_temp+layer.name+".tif"
                    else:
                        geotiff += "1.12/"+dir_temp+layer.name+".tif "
                else:
                    coastLine = layer.name
            
            # stringa per lo script
            data = " 1.12/apply_fprmcda_msf_comdline.R 1.12/"+dir_temp+" 1.12/"+dir_temp+"output/ "+name+" "+extent+" "+coastLine+" 1.12/components_cuts_grades_TR1224.csv 1.12/components_cuts_grades_TR2440.csv 1.12/components_cuts_grades_PS.csv "+dir_output+"/pairwise_matrix_TR.csv "+dir_output+"/pairwise_matrix_PS.csv "+dir_output+"/Fishing_Gear_TR1224.csv "+dir_output+"/Fishing_Gear_TR2440.csv "+dir_output+"/Fishing_Gear_PS.csv "+no_take_tr+" "+no_take_ps+" "+geotiff+""+fpc_ssf+"\n"
         
            # Create a socket (SOCK_STREAM means a TCP socket)
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

            try:
                # Connect to server and send data
                sock.connect((settings.R_HOST, settings.R_PORT))
                sock.sendall(data.encode('utf-8'))
                # Receive data from the server and shut down
                received = sock.recv(2048)
            except socket.error:
                #write error code to file
                logger.info ("Error:     %s" % socket.error)
            finally:
                sock.close()            
        
            logger.info ("Sent:     %s" % data.encode('utf-8'))
            logger.info ("Received: %s" % received)

            # copio il file di output nella cartella esposta su web
            src_files = os.listdir(directory+dir_temp+'output/')
            for file_name in src_files:
                full_file_name = os.path.join(directory+dir_temp+'output/', file_name)
                if os.path.isfile(full_file_name):
                    shutil.copy2(full_file_name, dir_output)

            # elimino la cartella temporanea
            shutil.rmtree(directory+dir_temp)

            if (received == '0'):
                self.stdout.write('success, name folder documents -> ['+strtoolr+']')
                if (id_tool):
                    tr = ToolsR_1_12.objects.filter(id=id_tool).update(status="completed")
            else:
                self.stdout.write('fail, error script. Check layers.')
            
        else:
            self.stdout.write('fail, directoy R Server with script not exist -> '+directory)