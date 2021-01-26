# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import coreapi
from django.core import serializers
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings
import os, traceback, datetime, tempfile, shutil, re, string, subprocess, sys, random, string

# Create your views here.
from rest_framework import generics
from rest_framework.views import APIView
from rest_framework.response import Response

from rest_framework.decorators import api_view, renderer_classes
from casestudies.models import CasestudiesToken


from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator

from django.core.serializers.json import DjangoJSONEncoder

#from casestudies.forms import CasestudiesListForm

try:
    import json
except ImportError:
    from django.utils import simplejson as json

from geonode.people.models import Profile 


def call_api(action, params):



    auth_api = CasestudiesToken.objects.get(is_enabled=True)
    auth = coreapi.auth.TokenAuthentication(
        scheme = 'Token',
        token = auth_api.token
    )
    client = coreapi.Client(auth=auth)

    # se action è un array (list) 
    if isinstance(action, list):  
        schema = client.get(auth_api.schema)
        return client.action(schema, action, params=params)
    else:  # se action è una stringa, url del file
        schema = client.get(action)
        return schema
        


def api_error(error_id):
    resp = {
        "error_code" : error_id
    }
    return resp



class RunCaseStudies(APIView): 
    def get(self, request):
        
        _id = ""
        _selected_layers = ""
        result = []

        if request.method == 'GET' and 'id' in request.GET:
            if (request.GET['id']):
                _id = request.GET['id']

                if request.method == 'GET' and 'selected_layers' in request.GET:
                    if (request.GET['selected_layers']):
                        _selected_layers = request.GET['selected_layers']

                result = call_api(
                    ["api", "casestudies", "run"],
                    params = {
                        "id": _id,
                        "selected_layers" : _selected_layers
                    }
                )
        
        return Response(
            {
                "geonode_version": "2.10", 
                "meta": {
                }, 
                "objects": result,
                "id" : _id                
            }
        )

class RunCaseStudy(APIView): 
    def get(self, request):
        _id = ""
        result = []
        if request.method == 'GET' and 'id' in request.GET:
            if (request.GET['id']):
                _id = request.GET['id']

                result = call_api(
                    ["api", "casestudyruns", "read"],
                    params = {
                        "id": _id
                    }
                )
        
        return Response(
            {
                "geonode_version": "2.10", 
                "meta": {
                }, 
                "objects": result,
                "id" : _id                
            }
        )

class CloneCaseStudy(APIView): 
    def post(self, request):
        _id = ""
        _label = ""
        _description = ""
        result = []
        if request.method == 'POST' and 'id' in request.POST:
            if (request.POST['id']):
                _id = request.POST['id']
            if (request.POST['label']):
                _label = request.POST['label']
            if (request.POST['description']):
                _description = request.POST['description']

            result = call_api(
                ["api", "casestudies", "cloneupdate"],
                params = {
                    "id": _id,
                    "label": _label,
                    "description": _description,
                    "tag" : request.user.username #attivare a modifica effettuata sul clone
                }
            )
        
        return Response(
            {
                "geonode_version": "2.10", 
                "meta": {
                }, 
                "objects": result
            }
        )



class DeleteLayersCaseStudy(APIView): 
    def post(self, request):
        _id = ""
        _url = ""
        result = []
        if request.method == 'POST' and 'id' in request.POST and 'url' in request.POST :
            if (request.POST['id']):
                _id = request.POST['id']
            

                result_cs = call_api(
                    ["api", "casestudies", "read"],
                    params = {
                        "id": _id,
                    }
                )

                if request.user.username != result_cs["tag"]:
                    return Response(
                    {
                        "geonode_version": "2.10", 
                        "meta": {
                        }, 
                        "objects": [],
                        "layers": [],
                        "success" : False
                    })

                if (request.POST['url']):
                    _url = request.POST['url']

                    auth_api = CasestudiesToken.objects.get(is_enabled=True)
                    import requests
                    result = requests.delete(_url, auth=('Token', auth_api.token))

                    result_cs = call_api(
                        ["api", "casestudies", "read"],
                        params = {
                            "id": _id,
                        }
                    )
                
                
                    return Response(
                        {
                            "geonode_version": "2.10", 
                            "meta": {}, 
                            "objects": result,
                            "layers" :  result_cs["layers"] ,
                            "success" : True

                        }
                    )


class EditCaseStudy(APIView): 
    def post(self, request):
        _id = ""
        _label = ""
        _description = ""
        result = []

        
        if request.method == 'POST' and 'id' in request.POST:
            if (request.POST['id']):
                _id = request.POST['id']

            result_cs = call_api(
                ["api", "casestudies", "read"],
                params = {
                    "id": _id,
                }
            )
            
            if request.user.username != result_cs["tag"]:
                return Response(
                {
                    "geonode_version": "2.10", 
                    "meta": {
                    }, 
                    "objects": [],
                    "success" : False
                })



            if (request.POST['label']):
                _label = request.POST['label']

            if (request.POST['description']):
                _description = request.POST['description']

            result = call_api(
                ["api", "casestudies", "partial_update"],
                params = {
                    "id": _id,
                    "label": _label,
                    "description": _description
                })
        
            return Response(
                {
                    "geonode_version": "2.10", 
                    "meta": {}, 
                    "objects": result,
                    "success" : True
                }
            )



class DeleteCaseStudy(APIView): 
    def post(self, request):
        _id = ""
        
        
        if request.method == 'POST' and 'id' in request.POST:
            if (request.POST['id']):
                _id = request.POST['id']

            result_cs = call_api(
                ["api", "casestudies", "read"],
                params = {
                    "id": _id,
                }
            )
            
            if request.user.username != result_cs["tag"]:
                return Response(
                {
                    "geonode_version": "2.10", 
                    "meta": {
                    }, 
                    "objects": [],
                    "success" : False
                })

            result = call_api(
                ["api", "casestudies", "delete"],
                params = {
                    "id": _id,
                })

            return Response(
                {
                    "geonode_version": "2.10", 
                    "meta": {}, 
                    "objects": result,
                    "success" : True
                }
            )



class ListInputs(APIView):
    def get(self, request):
        
        _file = ""
        if request.method == 'GET' and 'file' in request.GET:
            if (request.GET['file']):
                _file = request.GET['file']

        result = call_api(_file, params = {} )
        
        return Response(
            {
                "geonode_version": "2.10", 
                "meta": {}, 
                "objects": result                
            }
        )

class SetContext(APIView):
    def get(self, request):
        
        _id= ""
        _context_label = ""

        if request.method == 'GET' and 'id' in request.GET:
            if (request.GET['id']):
                _id = request.GET['id']
        
        if request.method == 'GET' and 'context_label' in request.GET:
            if (request.GET['context_label']):
                _context_label = request.GET['context_label']

        result = call_api(
            ["api" , "casestudies" , "setcontext"]
            , params = {
                "id": _id,
                "context_label": _context_label
        } )
        
        return Response(
            {
                "geonode_version": "2.10", 
                "meta": {}, 
                "objects": result                
            }
        )



class ListCodedlabels(APIView):
    def get(self, request):
        
        result = call_api(
            ["api", "codedlabels", "list"],
            params = {}
        )
        
        return Response(
            {
                "geonode_version": "2.10", 
                "meta": {}, 
                "objects": result                
            }
        )


class ListCasestudies(APIView):
    def get(self, request):
        
        _module = ""
        if request.method == 'GET' and 'module' in request.GET:
            if (request.GET['module']):
                _module = request.GET['module']
        

        _cstype = "default"
        if request.user.is_authenticated() and request.method == 'GET' and 'cstype' in request.GET:            
            _cstype = ""
            if (request.GET['cstype']):
                _cstype = request.GET['cstype']


        result = call_api(
            ["api", "casestudies", "list"],
            params = {
                "cstype": _cstype,
                "module": _module,
            }
        )

        for r in result:
            user = {}
            try:
                user_obj = Profile.objects.get(username=r["tag"]) 
                user = { 
                    'full_name' : user_obj.get_full_name() or user_obj.get_username()
                }
            except Profile.DoesNotExist:
                user = { 'full_name' : r["tag"] }
            
            r["pdm_owner"] = user
            
        
        _limit = ""
        if request.method == 'GET' and 'limit' in request.GET:            
            if (request.GET['limit']):
                _limit = request.GET['limit']

        _offset = ""
        if request.method == 'GET' and 'offset' in request.GET:            
            if (request.GET['offset']):
                _offset = request.GET['offset']        

        return Response(
            {
                "geonode_version": "2.10", 
                "meta": {
                    "limit": _limit, 
                    "offset": _offset, 
                    "total_count": len(result)
                }, 
                "objects": result                
            }
        )

class ReadCasestudies(APIView):
    def get(self, request, id):
        
        _id = id
        # if request.method == 'GET' and 'id' in request.GET:
        #     if (request.GET['id']):
        #         _id = request.GET['id']
        
        _module = ""
        if request.method == 'GET' and 'module' in request.GET:
            if (request.GET['module']):
                _module = request.GET['module']
        
        _cstype = ""
        if request.method == 'GET' and 'cstype' in request.GET:            
            if (request.GET['cstype']):
                _cstype = request.GET['cstype']


        result = call_api(
            ["api", "casestudies", "read"],
            params = {
                "id": _id,
                "cstype": _cstype,
                "module": _module,
            }
        )
        
        _limit = ""
        if request.method == 'GET' and 'limit' in request.GET:            
            if (request.GET['limit']):
                _limit = request.GET['limit']

        _offset = ""
        if request.method == 'GET' and 'offset' in request.GET:            
            if (request.GET['offset']):
                _offset = request.GET['offset']        

        return Response(
            {
                "geonode_version": "2.10", 
                "meta": {
                    "limit": _limit, 
                    "offset": _offset, 
                }, 
                "objects": result                
            }
        )


class CreateCaseStudy(APIView):
    def get(self, request):
        
        api_error_id = []

        _label = ""
        if request.method == 'GET' and 'label' in request.GET:
            if (request.GET['label']):
                _label = request.GET['label']
            else :
                api_error_id.append('label')
                

        _description = ""
        if request.method == 'GET' and 'description' in request.GET:            
            if (request.GET['description']):
                _description = request.GET['description']

        _module = ""
        if request.method == 'GET' and 'module' in request.GET:            
            if (request.GET['module']):
                _module = request.GET['module']
            else :
                api_error_id.append('module')

        _cstype = ""
        if request.method == 'GET' and 'cstype' in request.GET:            
            if (request.GET['cstype']):
                _cstype = request.GET['cstype']
            else :
                api_error_id.append('cstype')

        _resolution = 0
        if request.method == 'GET' and 'resolution' in request.GET:            
            if (request.GET['resolution']):
                _resolution = request.GET['resolution']
            else :
                api_error_id.append('resolution')
                
        _domain_area = None
        if request.method == 'GET' and 'domain_area' in request.GET:            
            if (request.GET['domain_area']):
                _domain_area = request.GET['domain_area']
            # else :
            #     api_error_id.append('domain_area')

        _domain_area_terms = []
        if request.method == 'GET' and 'domain_area_terms' in request.GET:            
            if (request.GET['domain_area_terms']):
                _domain_area_terms = request.GET['domain_area_terms']
            # else :
            #     api_error_id.append('domain_area_terms')

        _success = True

        if (len(api_error_id) > 0) :
            result = api_error(api_error_id)
            _success = False
        else: 
            # crea case study
            result = call_api( 
                ["api", "casestudies", "create"] 
                , 
                {
                    "label": _label,
                    "description": _description,
                    "module": _module,
                    "cstype": _cstype,
                    "resolution": _resolution,
                    "tag": request.user,
                    "domain_area": _domain_area,
                    "domain_area_terms": _domain_area_terms,
                }
            )
        
        _limit = ""
        if request.method == 'GET' and 'limit' in request.GET:            
            if (request.GET['limit']):
                _limit = request.GET['limit']

        _offset = ""
        if request.method == 'GET' and 'offset' in request.GET:            
            if (request.GET['offset']):
                _offset = request.GET['offset']        
        
        return Response(
            {
                "success" : _success,
                "geonode_version": "2.10", 
                "meta": {
                    "limit": _limit, 
                    "offset": _offset, 
                    "total_count": len(result)
                }, 
                "objects": result                
            }
        )

 
class CreateAndUploadJsonMatrix(APIView):
    def post(self, request):
        
        _name = ""
        if 'name' in request.POST:
            if (request.POST['name']):
                _name = request.POST['name']

        _data = ""
        if 'data' in request.POST:
            if (request.POST['data']):
                _data = request.POST['data']

        dir_json = settings.STATIC_ROOT + "json/"
        if not os.path.exists(dir_json):
            os.makedirs(dir_json)

        rndm = randomString(8)
        _jsonFileName = rndm + "_" + _name + ".json"
        _jsonFile = dir_json + _jsonFileName

        _success = False
        if ( _name is not None and _data is not None ) and ( _name is not '' and _data is not '' ) :
            with open(_jsonFile, "w") as out:
                out.write(_data)
                _success = True
        
        _resp = ""
        if _name is None or _name is '':
            _resp += "Nome mancante\n"
        
        if _data is None or _data is '':
            _resp += "Data mancante\n"

        # # upload thumbnail
        # if _thumbnailpath is not None:
        #     url = created_obj['url'] + 'tupload/'
        #     input_file = _thumbnailpath
        #     with open(input_file, 'rb') as f:
        #         files_t = {'file': f}
        #         t = requests.put(url, auth=('Token', auth_api.token), files=files_t)

        

        return Response(
            {
                "success" : _success,
                "geonode_version": "2.10", 
                "meta": {},
                "jsonFile" : _jsonFile,
                "resp" : _resp,
                "name" : _name
            }
        )


class CreateAndUpload(APIView):
    def put(self, request):
        
        #_id = id
        # if request.method == 'POST' and 'id' in request.POST:
        #     if (request.POST['id']):
        #         _id = request.POST['id']
        # url completo con id inputs

        _otype = ""
        if 'otype' in request.POST:
            if (request.POST['otype']):
                _otype = request.POST['otype']
        
        _parent_id = ""
        if 'parent_id' in request.POST:            
            if (request.POST['parent_id']):
                _parent_id = request.POST['parent_id']
                
        _clurl = ""
        if 'clurl' in request.POST:            
            if (request.POST['clurl']):
                _clurl = request.POST['clurl']

        _filepath = ""
        if 'filepath' in request.POST:            
            if (request.POST['filepath']):
                _filepath = request.POST['filepath']          
        
        _url = ""
        if 'url' in request.POST:            
            if (request.POST['url']):
                _url = request.POST['url']        

        _thumbnailpath = None
    
        if _url == "":
            created_obj = call_api( 
                ["api", "casestudies", _otype, "create"] 
                , 
                {
                    'parent_lookup_casestudy__id': _parent_id,
                    'coded_label': _clurl
                }
            )
        else :
            created_obj = call_api( 
                _url
                , 
                {
                    'parent_lookup_casestudy__id': _parent_id,
                    'coded_label': _clurl
                }
            )
        
        auth_api = CasestudiesToken.objects.get(is_enabled=True)
        
        import requests

        r = []
        t = []
        # upload file 
        if _filepath is not None:
            url = created_obj['url'] + 'upload/'
            input_file = _filepath
            with open(input_file, 'rb') as f:
                files = {'file': f}
                r = requests.put(url, auth=('Token', auth_api.token), files=files)
            

        # # upload thumbnail
        if _thumbnailpath is not None:
            url = created_obj['url'] + 'tupload/'
            input_file = _thumbnailpath
            with open(input_file, 'rb') as f:
                files_t = {'file': f}
                t = requests.put(url, auth=('Token', auth_api.token), files=files_t)

        _success = True

        return Response(
            {
                "success" : _success,
                "geonode_version": "2.10", 
                "meta": {}, 
                "objects": r,
                "objects_t": t,
            }
        )
        



def randomString(stringLength=6):
    """Generate a random string of fixed length """
    letters = string.ascii_lowercase
    return ''.join(random.choice(letters) for i in range(stringLength))