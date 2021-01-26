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

from geonode.utils import (resolve_object,get_dir_time_suffix,zip_dir)
from geonode.layers.models import Layer, LayerFile
from geonode.people.utils import get_valid_user

from osgeo import gdal

import os, traceback, datetime, tempfile, shutil, re, string, subprocess, sys, random, json, ntpath
#from PIL import Image

import logging
logger = logging.getLogger("geonode.documents.views")
gdal
def getFileToId(resourceid, directory_temp, grid, res, attribute):
    layers = Layer.objects.filter(id=resourceid)
    
    if layers:
        instance = layers[0]

    if isinstance(instance, Layer):
        try:
            upload_session = instance.get_upload_session()
            layer_files = [item for idx, item in enumerate(LayerFile.objects.filter(upload_session=upload_session))]
            result = ""
            for l in layer_files:
                if storage.exists(l.file):
                    geonode_layer_path = storage.path(l.file)
                    base_filename, original_ext = os.path.splitext(geonode_layer_path)
                    filename = ntpath.basename(geonode_layer_path)
                    filename_only, original_ext = os.path.splitext(filename)
                    if(not instance.is_vector() or (instance.is_vector() and original_ext.lower() == '.shp')):
                        if instance.is_vector():
                            if not os.path.exists(directory_temp+'rasterize/'):
                                os.makedirs(directory_temp+'rasterize/')
                            bbox = str(instance.bbox_x0)+ ' '+str(instance.bbox_y0)+ ' '+str(instance.bbox_x1)+ ' '+str(instance.bbox_y1)
                            resolution = str(res)
                            srs = instance.srid
                            if (grid):
                                grid_json = json.loads(grid)
                                resolution = str(grid_json["resolution"])
                                srs = "EPSG:"+str(grid_json["epsg"])
                            insert_value = "-burn 1"
                            if (attribute):
                                insert_value = "-a "+attribute

                            command_reproject = ['ogr2ogr' + ' -t_srs '+srs + ' ' + directory_temp + 'rasterize/reprojected.shp' + ' ' + geonode_layer_path]
                            logger.info('ogr2ogr' + ' -t_srs '+srs + ' ' + directory_temp + 'rasterize/reprojected.shp' + ' ' + geonode_layer_path)
                     
                            result_reproject = subprocess.check_output(command_reproject, shell=True)
                        
                            command = ['gdal_rasterize -te '+bbox+ ' -a_srs '+srs+' -tr '+resolution+' '+resolution+' -tap '+insert_value+' -l reprojected '+directory_temp + 'rasterize/'+' '+directory_temp+'rasterize/'+filename_only+'.tif']
                            logger.info('gdal_rasterize -te '+bbox+ ' -a_srs '+srs+' -tr '+resolution+' '+resolution+' -tap '+insert_value+' -l reprojected '+directory_temp + 'rasterize/'+' '+directory_temp+'rasterize/'+filename_only+'.tif')
                             
                            result_rasterize = subprocess.check_output(command, shell=True) 
                            
                            if result_rasterize.find('100 - done') != -1:
                                geonode_layer_path = directory_temp+'rasterize/'+filename_only+'.tif'
                                filename = filename_only+'.tif'
                            else:
                                return 'ERROR:' + result_rasterize
                        
                        if (grid):
                            shutil.copy2(geonode_layer_path, directory_temp)
                            grid_json = json.loads(grid)
                            filename_tmp = randomString(8)
                            command = ['gdalwarp -te '+str(grid_json["bounds"][0])+ ' '+str(grid_json["bounds"][1])+ ' '+str(grid_json["bounds"][2])+ ' '+str(grid_json["bounds"][3])+ ' -te_srs EPSG:'+str(grid_json["epsg"])+ ' -tr '+str(grid_json["resolution"])+' '+str(grid_json["resolution"])+' -tap ' + directory_temp+filename + ' '+directory_temp+'output/'+filename_tmp]
                            result = subprocess.check_output(command, shell=True) 
                            if result.find('100 - done') != -1:
                                result = directory_temp+'output/'+filename_tmp
                            else:
                                return 'ERROR:' + result
                        else:
                            result = geonode_layer_path
                                       
            return result
                
        except NotImplementedError:
            traceback.print_exc()
            tb = traceback.format_exc()
            logger.debug(tb)
            return "file not found"
        
    else:
        return "layer not found"

def getNumbers(str): 
    #array = re.findall(r"[-+]?\d*\.\d+|\d+", str) 
    array = re.findall(r"\d*\.\d+|\d+", str) 
    return array 

def getCheckAttributes(str): 
    array = re.split('\++|/+|-+|\*+|\(+|\)+|MAX+|MIN+|AVG+|LOG+|RESIZE+|MASK_LESS+|MASK_GREAT|,',str)
    return list(filter(lambda a: a != "", array))

def replaceStrFunctions(str): 
    str = str.replace("MAX","numpy.max") 
    str = str.replace("MIN","numpy.min") 
    str = str.replace("AVG","numpy.average") 
    str = str.replace("LOG","numpy.log") 
    str = str.replace("RESIZE","numpy.resize")
    str = str.replace("MASK_LESS","ma.masked_less")
    str = str.replace("MASK_GREAT","ma.masked_greater")
    return str

def representsInt(s):
    try: 
        int(s)
        return True
    except ValueError:
        return False

def randomString(stringLength=10):
    """Generate a random string of fixed length """
    letters = string.ascii_lowercase
    return ''.join(random.choice(letters) for i in range(stringLength))

class Command(BaseCommand):
    help = ("PDM: Expression layers....")

    def add_arguments(self, parser):
      
        # Named (optional) arguments
        parser.add_argument(
            '-ex',
            '--expression',
            dest="expression",
            default=None,
            help="Expression")

        parser.add_argument(
            '-gr',
            '--grid',
            dest="grid",
            default=None,
            help="Grid")
        
        parser.add_argument(
            '-res',
            '--resolution',
            dest="resolution",
            default=0.01,
            help="Resolution")
        
        # Named (optional) arguments
        parser.add_argument(
            '-d',
            '--directory',
            dest="directory",
            default="/mnt/volumes/statics/static/result_expressions/",
            help="Directory expression layer file")

        parser.add_argument(
            '-o',
            '--output',
            dest="output",
            default="/mnt/volumes/statics/uploaded/result_expressions/",
            help="Directory output files")
        
            

    def handle(self, *args, **options):

        expression = options.get('expression', None)
        
        grid = options.get('grid', None)
        resolution = options.get('resolution', None)
        
        directory = options.get('directory', None)
        output = options.get('output', None)

        list_numbers = getNumbers(expression) 
        check_attributes = getCheckAttributes(expression) 
        
        alph = list(string.ascii_uppercase)

        if not directory:
            directory = tempfile.mkdtemp()  

        dir_temp = tempfile.mkdtemp()[1:]+'/'
        if not os.path.exists(directory+dir_temp+'output/'):
            os.makedirs(directory+dir_temp+'output/')
        
        i = 0
        replacements = {}
        str_input = ""
        for num in list_numbers: 
            if (representsInt(num)):
                attribute = None
                if "#" in check_attributes[i]:
                    attribute = check_attributes[i].split("#")[1]
                filename = getFileToId(num, directory+dir_temp, grid, resolution, attribute)
                if filename.find('ERROR:') == -1:
                    str_input += '-'+alph[i]+' '+filename+' '
                    replacements[num] = alph[i]
                    i+=1
                else:
                    self.stdout.write(filename)
                    return None 

        def replTxt(match):
            return replacements[match.group()] if representsInt(match.group()) else match.group()

        i=0
        expr_without_attr = expression
        for attr in check_attributes:
            expr_without_attr = expr_without_attr.replace(attr,list_numbers[i])
            i=i+1
        expr_without_attr = replaceStrFunctions(expr_without_attr)
        a = re.compile(r"[-+]?\d*\.\d+|\d+")  
        converted_expression = a.sub(replTxt, expr_without_attr).replace('.0','')
        
        if not output:
            output = tempfile.mkdtemp()
        
        if not os.path.exists(output):
            os.makedirs(output)

        filename = randomString(8)
        result_tif = 'result_'+filename+'.geotiff'
        
        command = ['gdal_calc.py '+str_input+ '--outfile=' + output + result_tif + ' --calc="'+converted_expression.replace("'", "")+'"']
        #logger.info('gdal_calc.py '+str_input+ '--outfile=' + output + result_tif + ' --calc="'+converted_expression.replace("'", "")+'"')
        result = subprocess.check_output(command, shell=True) 

        shutil.rmtree(directory+dir_temp)
        
        if result.find('100 - Done') != -1:
            self.stdout.write('success:'+result_tif)
        else:
            self.stdout.write(result)  
        