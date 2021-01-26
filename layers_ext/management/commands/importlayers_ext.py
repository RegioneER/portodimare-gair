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

import os
from django.utils import timezone
from django.core.management import call_command
from django.core.management.base import BaseCommand
from layers_ext.utils import upload
from geonode.people.utils import get_valid_user
import traceback
import datetime

import logging
logger = logging.getLogger("geonode.documents.views")

def setLayersPermissions(resources, groups, permission):
    call_command('set_layers_permissions', \
        resources=resources.split(" "), \
        groups=groups.split(" "), \
        permission=permission)

class Command(BaseCommand):
    help = ("PDM: Brings a data file or a directory full of data files into a"
            " GeoNode site.  Layers are added to the Django database, the"
            " GeoServer configuration, and the pycsw metadata index.")

    def add_arguments(self, parser):
        # Positional arguments
        parser.add_argument('path', nargs='*', help='path [path...]')

        # Named (optional) arguments
        parser.add_argument(
            '-u',
            '--user',
            dest="user",
            default=None,
            help="Name of the user account which should own the imported layers")

        parser.add_argument(
            '-i',
            '--ignore-errors',
            action='store_true',
            dest='ignore_errors',
            default=False,
            help='Stop after any errors are encountered.')

        parser.add_argument(
            '-o',
            '--overwrite',
            dest='overwrite',
            default=False,
            action="store_true",
            help="Overwrite existing layers if discovered (defaults False)")

        parser.add_argument(
            '-k',
            '--keywords',
            dest='keywords',
            default="",
            help=("The default keywords, separated by comma, for the imported"
                  " layer(s). Will be the same for all imported layers"
                  " if multiple imports are done in one command"))

        parser.add_argument(
            '-l',
            '--license',
            dest='license',
            default=None,
            help=("The license for the imported layer(s). Will be the same for"
                  " all imported layers if multiple imports are done"
                  " in one command"))

        parser.add_argument(
            '-c',
            '--category',
            dest='category',
            default=None,
            help=("The category for the imported layer(s). Will be the same"
                  " for all imported layers if multiple imports are done"
                  " in one command"))

        parser.add_argument(
            '-r',
            '--regions',
            dest='regions',
            default="",
            help=("The default regions, separated by comma, for the imported"
                  " layer(s). Will be the same for all imported layers if"
                  " multiple imports are done in one command"))

        parser.add_argument(
            '-n',
            '--name',
            dest='layername',
            default=None,
            help="The name for the imported layer(s). Can not be used with multiple imports")

        parser.add_argument(
            '-t',
            '--title',
            dest='title',
            default=None,
            help=("The title for the imported layer(s). Will be the same for"
                  " all imported layers if multiple imports are done"
                  " in one command"))

        parser.add_argument(
            '-a',
            '--abstract',
            dest='abstract',
            default=None,
            help=("The abstract for the imported layer(s). Will be the same for"
                  "all imported layers if multiple imports are done"
                  "in one command"))

        parser.add_argument(
            '-si',
            '--supplemental_information',
            dest='supplemental_information',
            default=None,
            help=("The supplemental_information for the imported layer(s). Will be the same for"
                  "all imported layers if multiple imports are done"
                  "in one command"))

        parser.add_argument(
            '-d',
            '--date',
            dest='date',
            default=None,
            help=('The date and time for the imported layer(s). Will be the '
                  'same for all imported layers if multiple imports are done '
                  'in one command. Use quotes to specify both the date and '
                  'time in the format \'YYYY-MM-DD HH:MM:SS\'.'))

        parser.add_argument(
            '-p',
            '--private',
            dest='private',
            default=False,
            action="store_true",
            help="Make layer viewable only to owner")

        parser.add_argument(
            '-m',
            '--metadata_uploaded_preserve',
            dest='metadata_uploaded_preserve',
            default=False,
            action="store_true",
            help="Force metadata XML to be preserved")

        parser.add_argument(
            '-C',
            '--charset',
            dest='charset',
            default='UTF-8',
            help=("Specify the charset of the data"))
        
        parser.add_argument(
            '-sp',
            '--spatial_representation_type',
            dest='spatial_representation_type',
            default="",
            help=("The spatial representation for the imported layer(s). Will be the same"
                  " for all imported layers if multiple imports are done"
                  " in one command"))
        
        parser.add_argument(
            '-tes',
            '--temporal_extent_start',
            dest='temporal_extent_start',
            default=None,
            help=('The temporal extent start for the imported layer(s). Will be the '
                  'same for all imported layers if multiple imports are done '
                  'in one command. Use quotes to specify both the date and '
                  'time in the format \'YYYY-MM-DD HH:MM:SS\'.'))
        
        parser.add_argument(
            '-tee',
            '--temporal_extent_end',
            dest='temporal_extent_end',
            default=None,
            help=('The temporal extent end for the imported layer(s). Will be the '
                  'same for all imported layers if multiple imports are done '
                  'in one command. Use quotes to specify both the date and '
                  'time in the format \'YYYY-MM-DD HH:MM:SS\'.'))

        parser.add_argument(
            '-da',
            '--domain_area',
            dest='domain_area',
            default="",
            help=("The default domain areas, separated by comma, for the imported"
                  " layer(s). Will be the same for all imported layers if"
                  " multiple imports are done in one command"))
        
        parser.add_argument(
            '-dp',
            '--data_portal',
            dest='data_portal',
            default=None,
            help=("The data portal for the imported layer(s). Will be the same"
                  " for all imported layers if multiple imports are done"
                  " in one command"))
        
        parser.add_argument(
            '-vl',
            '--validation_level',
            dest='validation_level',
            default=None,
            help=("The validation level for the imported layer(s). Will be the same"
                  " for all imported layers if multiple imports are done"
                  " in one command"))
        
        parser.add_argument(
            '-ac',
            '--data_accessibility',
            dest='data_accessibility',
            default=None,
            help=("The data accessibility for the imported layer(s). Will be the same"
                  " for all imported layers if multiple imports are done"
                  " in one command"))
        
        parser.add_argument(
            '-st',
            '--starred',
            dest='starred',
            default=None,
            help=("The starred for the imported layer(s). Will be the same"
                  " for all imported layers if multiple imports are done"
                  " in one command (True or 1 -> true)"))

        parser.add_argument(
            '-dir',
            '--directory',
            dest="directory",
            default='/var/log/importlayers',
            help="import directory")

        parser.add_argument(
            '-log',
            '--log',
            dest='log',
            default='import.log',
            help=("log file import"))
        
        parser.add_argument(
            '-g',
            '--groups',
            dest='groups',
            nargs='*',
            type=str,
            default=None,
            help='Groups for which permissions will be assigned to. '
                 'Multiple choices can be typed with white space separator.'
        )

        parser.add_argument(
            '-pm',
            '--permission',
            dest='permission',
            type=str,
            default=None,
            help='Permissions to be assigned. '
                 'Allowed values are: read (r), write (w), download (d) and owner (o).'
        )

         

    def handle(self, *args, **options):

        verbosity = int(options.get('verbosity'))
        # ignore_errors = options.get('ignore_errors')
        username = options.get('user')
        user = get_valid_user(username)
        overwrite = options.get('overwrite')
        name = options.get('layername', None)
        title = options.get('title', None)
        abstract = options.get('abstract', None)
        supplemental_information = options.get('supplemental_information', None)
        date = options.get('date', None)
        license = options.get('license', None)
        category = options.get('category', None)
        private = options.get('private', False)
        metadata_uploaded_preserve = options.get('metadata_uploaded_preserve',
                                                 False)
        charset = options.get('charset', 'UTF-8')

        spatial_representation_type = options.get('spatial_representation_type', None)

        temporal_extent_start = options.get('temporal_extent_start', None), 
        if temporal_extent_start:
            if temporal_extent_start[0] is not None:
                temporal_extent_start = datetime.datetime.strptime(temporal_extent_start[0], '%Y-%m-%d')
            else:
                temporal_extent_start = None
        
        temporal_extent_end = options.get('temporal_extent_end', None), 
        if temporal_extent_end:
            if temporal_extent_end[0] is not None:
                temporal_extent_end = datetime.datetime.strptime(temporal_extent_end[0], '%Y-%m-%d')
            else:
                temporal_extent_end = None
        
        data_portal = options.get('data_portal', None)
        validation_level = options.get('validation_level', None)
        data_accessibility = options.get('data_accessibility', None)
        starred = options.get('starred', None)

        directory = options.get('directory', None)
        log = options.get('log', None)

        groups = options.get('groups', None)
        permission = options.get('permission', None)

        if not os.path.exists(directory):
            os.makedirs(directory)

        f = open(directory + '/' + log, "a")

        if verbosity > 0:
            console = self.stdout
        else:
            console = None

        if overwrite:
            skip = False
        else:
            skip = True

        keywords = options.get('keywords').encode("utf-8").split(',')
        if len(keywords) == 1 and keywords[0] == '':
            keywords = []
        else:
            keywords = map(str.strip, keywords)
        
        regions = options.get('regions').encode("utf-8").split(',')
        if len(regions) == 1 and regions[0] == '':
            regions = []
        else:
            regions = map(str.strip, regions)

        domain_area = options.get('domain_area').encode("utf-8").split(',')
        if len(domain_area) == 1 and domain_area[0] == '':
            domain_area = []
        else:
            domain_area = map(str.strip, domain_area)
       
        start = datetime.datetime.now(timezone.get_current_timezone())
        output = []
        
        for path in options['path']:
            out = upload(
                path,
                user=user,
                overwrite=overwrite,
                skip=skip,
                name=name,
                title=title,
                abstract=abstract,
                supplemental_information=supplemental_information,
                spatial_representation_type=spatial_representation_type,
                temporal_extent_start=temporal_extent_start, 
                temporal_extent_end=temporal_extent_end, 
                date=date,
                keywords=keywords,
                verbosity=verbosity,
                console=console,
                license=license,
                category=category,
                regions=regions,
                domain_area=domain_area,
                data_portal=data_portal,
                validation_level=validation_level,
                data_accessibility=data_accessibility,
                starred=starred,
                private=private,
                metadata_uploaded_preserve=metadata_uploaded_preserve,
                charset=charset)

            output.extend(out)
       

        updated = [dict_['file']
                   for dict_ in output if dict_['status'] == 'updated']
        created = [dict_['file']
                   for dict_ in output if dict_['status'] == 'created']
        skipped = [dict_['file']
                   for dict_ in output if dict_['status'] == 'skipped']
        failed = [dict_['file']
                  for dict_ in output if dict_['status'] == 'failed']

        finish = datetime.datetime.now(timezone.get_current_timezone())
        td = finish - start
        duration = td.microseconds / 1000000 + td.seconds + td.days * 24 * 3600
        duration_rounded = round(duration, 2)
        
        f.write("\n================\n")
        f.write("-> IMPORT LAYERS ("+str(finish)+")\n")

        if not output:
            f.write("NO IMPORT -> "+name+"\n")
            f.write(path+"\n")
       
        for dict_ in output:
            if not dict_['status'] == 'failed':
                f.write("\n"+dict_['name']+"\n")
                # CHANGE PERMISSION GROUP (PDM)
                if (groups and permission):
                    setLayersPermissions(dict_['name'], groups, permission)
            if (dict_['file']):
                f.write("file: "+dict_['file']+"\n")
            f.write("status: "+dict_['status']+"\n")
            if dict_['status'] == 'failed':
                traceback.print_exception(dict_['exception_type'],
                                              dict_['error'],
                                              dict_['traceback'],
                                              limit=2, file=f)
                

        if verbosity > 1:
            print "\nDetailed report of failures:"
            for dict_ in output:
                if dict_['status'] == 'failed':
                    print "\n\n", dict_['file'], "\n================"
                    traceback.print_exception(dict_['exception_type'],
                                              dict_['error'],
                                              dict_['traceback'])

        if verbosity > 0:
            print "\n\nFinished processing %d layers in %s seconds.\n" % (
                len(output), duration_rounded)
            print "%d Created layers" % len(created)
            print "%d Updated layers" % len(updated)
            print "%d Skipped layers" % len(skipped)
            print "%d Failed layers" % len(failed)

            if len(output) > 0:
                print "%f seconds per layer" % (duration * 1.0 / len(output))