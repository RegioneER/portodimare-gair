# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import coreapi
from django.shortcuts import render
from datetime import datetime
# Create your views here.
from django.views.generic import DetailView
from django.conf import settings

from .models import CasestudiesToken, CasestudiesModule, CasestudiesCsType
from geodatabuilder.models import GeoDataBuilder

from base_ext.models import DomainArea
from django.contrib.auth.decorators import login_required
import json
from django.core.serializers.json import DjangoJSONEncoder

from geonode.people.models import Profile 



def casestudies(request):
    """This view shows the list of all registered services"""
    
    return render(
        request,
        "casestudies/casestudies_list.html",
        {
            "modules" : CasestudiesModule.objects.all(),
            "cstype" : CasestudiesCsType.objects.all(),            
        }
    )


def call_api(action, params):
    auth_api = CasestudiesToken.objects.get(is_enabled=True)
    auth = coreapi.auth.TokenAuthentication(
        scheme = 'Token',
        token = auth_api.token
    )
    client = coreapi.Client(auth=auth)
    schema = client.get(auth_api.schema)
    
    return client.action(schema, action, params=params)

def casestudies_detail(request, id):   
    
    

    cs_type_str = "default"
    if request.user.is_authenticated():
        cs_type_str = "" 

    # dettaglio di un case study
    result = call_api( 
        ["api", "casestudies", "read"] 
        , 
        {
            "id": id,
            "cstype": cs_type_str,
            "module": "",
        }
    )
    
    try:
        result["pdm_owner"] = Profile.objects.get(username=result["tag"])
    except Profile.DoesNotExist:
        result["pdm_owner"] = result["tag"]



    resp = {
        "geonode_version": "2.10", 
        "meta": {}, 
        "objects": result        
    }
    
    

    # modificare il formato data
    # if resp["objects"]["created"]:
    #     _created = resp["objects"]["created"]
    #     _created = datetime._created.strftime("%Y")
    #     resp["objects"]["created"] = _created

    return render(
        request, 
        "casestudies/casestudies_detail.html" ,
        {
            "item" :  resp["objects"], 
            "layers" :  json.dumps(list(resp["objects"]["layers"]), cls=DjangoJSONEncoder) ,
            "expressions" : json.dumps(list( GeoDataBuilder.objects.filter(casestudy_api_id=id).values('id', 'label' , 'desc_expression' , 'expression' , 'expression_id_string' , 'updated' , 'file_path' ) ), cls=DjangoJSONEncoder),
            "expressionlayers_url" : settings.EXPRESSIONLAYERS_URL,
            "expressionlayers_path" : settings.EXPRESSIONLAYERS_PATH
        }
    )


@login_required
def casestudies_create(request):   
    
    return render(
        request,
        "casestudies/casestudies_create.html",
        {
            "modules" : CasestudiesModule.objects.all(),
            "cstype" : CasestudiesCsType.objects.all(),            
        }
    )




# def save_cs(request):

#     # if not request.user.has_perm('backend.add_artist'):
#     #     raise PermissionDenied

#     result = False
#     if request.method == 'POST':
#         form = CasestudiesListForm(data=request.POST)
#         result = form.is_valid()
#         if result:
#             object = form.save()
#             if not request.is_ajax():
#                 # reload the page
#                 next = request.META['PATH_INFO']
#                 # return HttpResponseRedirect(next)
#             # if is_ajax(), we just return the validated form, so the modal will close
#     else:
#         form = CasestudiesListForm()

#     return Response(
#         {            
#             "success": result                
#         }
#     )





class CasestudiesDetail(DetailView):

    model = CasestudiesToken
