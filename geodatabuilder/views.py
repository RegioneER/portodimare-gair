# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import coreapi
from django.shortcuts import render

from django.views.generic import DetailView
from django.views.generic.edit import UpdateView, CreateView, DeleteView
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, HttpResponseRedirect, Http404, JsonResponse
from django.core.urlresolvers import reverse
from django.shortcuts import render, redirect, get_object_or_404
from django.core.exceptions import PermissionDenied
from django.core.management import call_command

from rest_framework import generics, status
from rest_framework.views import APIView
from rest_framework.response import Response

from .forms import GeoDataBuilderForm
from .models import GeoDataBuilder
from django.contrib import messages
from django.contrib.messages import get_messages

from django.conf import settings
ALLOWED_DOC_TYPES = settings.ALLOWED_DOCUMENT_TYPES

from geonode.utils import resolve_object
from django.utils.translation import ugettext as _

import json, datetime

import urlparse

# Create your views here.
import logging
import StringIO

from casestudies.models import CasestudiesToken

from django.core import serializers

from coreapi.exceptions import CoreAPIException

from django.core.paginator import Paginator, InvalidPage

# from .utils import (

logger = logging.getLogger("geonode.geodatabuilder.views")

_NOT_ALLOWED = _("Not allowed")
_PERMISSION_MSG_DELETE = _("You are not permitted to delete this GeoDataBuilder")
_PERMISSION_MSG_DELETE_ALLOWED = _("You are not allowed to delete this GeoDataBuilder")
_PERMISSION_MSG_GENERIC = _("You do not have permissions for this GeoDataBuilder.")
_PERMISSION_MSG_MODIFY = _("You are not permitted to modify this GeoDataBuilder")
_PERMISSION_MSG_METADATA = _(
    "You are not permitted to modify this GeoDataBuilder's metadata")
_PERMISSION_MSG_VIEW = _("You are not permitted to view this GeoDataBuilder")


def _resolve_geodatabuilder(request, id, permission='base.change_resourcebase',
                      msg=_PERMISSION_MSG_GENERIC, **kwargs):
    '''
    Resolve the GeoDataBuilder by the provided primary key and check the optional permission.
    '''
    return resolve_object(request, GeoDataBuilder, {'id': id},
                          permission=permission, permission_msg=msg, **kwargs)


def get_current_user(request):
    current_user = request.user
    return current_user

def geodatabuilder_list(request):

    m = ""
    messages = get_messages(request)
    for message in messages:
        m = str(m) +  str(message) + str("<br />")
    
    
    query_param = {}

    _limit = settings.CLIENT_RESULTS_LIMIT
    _offset = "0"
    _owner = ""
    _label = ""
    _created = ""
    _order_by = "-updated"
    _page = "1"

    # if request.method == 'GET' and 'limit' in request.GET:
    #     if (request.GET['limit']):
    #         _limit = request.GET['limit']
    # if request.method == 'GET' and 'offset' in request.GET:
    #     if (request.GET['offset']):
    #         _offset = request.GET['offset']
    if request.method == 'GET' and 'page' in request.GET:
        if (request.GET['page']):
            _page = request.GET['page']
    
    if request.method == 'GET' and 'owner' in request.GET:
        if (request.GET['owner']):
            _owner = request.GET['owner']
            if len( _owner ) > 0:
                _owner_obj = get_user_model().objects.get(username=_owner)
                query_param["owner"] = _owner_obj.id
    
    if request.method == 'GET' and 'label' in request.GET:
        if (request.GET['label']):
            _label = request.GET['label']
            query_param["label__icontains"] = _label

    if request.method == 'GET' and 'order_by' in request.GET:
        if (request.GET['order_by']):
            _order_by = request.GET['order_by']

    
    
    
    # if request.method == 'GET' and 'created' in request.GET:
    #     if (request.GET['created']):
    #         _created = request.GET['created']
    #         query_param["created"] = _created

    geodatabuilders = GeoDataBuilder.objects.filter( **query_param ).order_by(_order_by)
    # geodatabuilders = GeoDataBuilder.objects.filter( **query_param )[_limit:_offset]

    
    
    geodatabuilders_user = GeoDataBuilder.objects.order_by("owner").distinct('owner')
    
    owners = []
    owners_sort = []
    for g in geodatabuilders_user:
        user = {}
        user["owner"] = g.owner
        user["full_name"] = g.owner.get_full_name() or g.owner.get_username()
        user["username"] = g.owner.get_username()
        user["tot"] = GeoDataBuilder.objects.filter( owner=g.owner).count()
        owners.append( user )
    
    # owners_sort = owners.sort(key=lambda x: x["full_name"])
    owners_sort = sorted(owners , key = lambda x: x["full_name"] )

    for g in geodatabuilders:
        cs = call_api( 
            ["api", "casestudies", "read"] 
            , 
            {
                "id": g.casestudy_api_id,
                "cstype": "",
                "module": "",
            }
        )
        g.casestudy = cs

    paginator = Paginator(geodatabuilders, _limit)

    next_page = 0
    previous_page = 0
    total_count = 0
    num_pages = paginator.num_pages
    items = []
    # current_page = int(_offset or 0) / int(_limit, 0) + 1
    current_page = _page

    try:
        page = paginator.page(current_page)
        # previous_page_number = page.previous_page_number()
        # next_page_number = page.next_page_number()
        
        items = page.object_list
    
    except InvalidPage:
        _page = "1"
        current_page = _page
        page = paginator.page(_page)
        #raise Http404("Sorry, no results on that page.")

    if page.has_previous():
        previous_page = page.previous_page_number()
    else:
        previous_page = 1

    if page.has_next():
        next_page = page.next_page_number()
    else:
        next_page = 1
    
    total_count = geodatabuilders.count()

    return render(
        request,
        "geodatabuilder/geodatabuilder_list.html",
        { 
            
            "current_page": current_page,
            "num_pages": num_pages,
            "next": next_page,
            "previous": previous_page,
            "total_count": total_count,
            "items": items,
            "debug": "",
            "geodatabuilders_user" : geodatabuilders_user,
            "owners" : owners_sort
        }
    )


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
        try:
            call = client.action(schema, action, params=params)
        except coreapi.exceptions.ErrorMessage as exc:
            resp = api_error( exc.error )
        else:
            resp = call
        return resp

    else:  # se action è una stringa, url del file
        schema = client.get(action)
        return schema
        


def api_error(error_id):
    resp = {
        "error_code" : error_id
    }
    return resp


def geodatabuilder_detail(request, id):
    """This view shows the list of all registered services"""
    
    geodatabuilder = get_object_or_404(GeoDataBuilder, id=id)
    
    return render(request, "geodatabuilder/geodatabuilder_detail.html", {
        "geodatabuilder": geodatabuilder,
        "user": get_current_user(request)
    })

def geodatabuilder_edit(request, id):
    """This view shows the list of all registered services"""
    
    geodatabuilder = get_object_or_404(GeoDataBuilder, id=id)
    if get_current_user(request) == geodatabuilder.owner :
        return render(request, "geodatabuilder/geodatabuilder_create.html", {
            "geodatabuilder": geodatabuilder,
            "user": get_current_user(request)
        })
    else :
        return HttpResponseRedirect(
                reverse(
                    'geodatabuilder_detail',
                    args=(id,)))
    

def geodatabuilder_create(request):
    """This view shows the list of all registered services"""
    
    return render(
        request,
        "geodatabuilder/geodatabuilder_create.html"
    )

def geodatabuilder_clone(request, id):
    """This view shows the list of all registered services"""
    
    geodatabuilder = get_object_or_404(GeoDataBuilder, id=id)
    geodatabuilder.id = None
    

    _label = geodatabuilder.label
    if 'label' in request.POST:
        if (request.POST['label']):
            _label = request.POST['label']
    geodatabuilder.label = _label

    _desc_expression = geodatabuilder.desc_expression
    if 'desc_expression' in request.POST:
        if (request.POST['desc_expression']):
            _desc_expression = request.POST['desc_expression']
    geodatabuilder.desc_expression = _desc_expression

    geodatabuilder.owner = request.user
    geodatabuilder.updated = datetime.datetime.now()
    geodatabuilder.save()

    return HttpResponseRedirect(
        reverse(
            'geodatabuilder_detail',
            args=(geodatabuilder.id,)))

class GeoDataBuilderCreate(CreateView):
    template_name = 'geodatabuilder/geodatabuilder_create.html'
    form_class = GeoDataBuilderForm

    def get_context_data(self, **kwargs):
        context = super(GeoDataBuilderCreate, self).get_context_data(**kwargs)
        context['ALLOWED_DOC_TYPES'] = ALLOWED_DOC_TYPES
        return context

    def form_invalid(self, form):
        if self.request.GET.get('no__redirect', False):
            out = {'success': False}
            out['message'] = ""
            status_code = 400
            return HttpResponse(
                json.dumps(out),
                content_type='application/json',
                status=status_code)
        else:
            form.label = None
            form.expression = None
            form.casestudy_api_id = None
            return self.render_to_response(self.get_context_data(form=form))

    def form_valid(self, form):
        """
        If the form is valid, save the associated model.
        """
        self.object = form.save(commit=False)
        self.object.owner = self.request.user
        self.object.save()
        
        out = {'success': False}

        if self.request.GET.get('no__redirect', False):
            out['success'] = True
            out['url'] = reverse(
                'geodatabuilder_detail',
                args=(
                    self.object.id,
                ))
            if out['success']:
                status_code = 200
            else:
                status_code = 400
            return HttpResponse(
                json.dumps(out),
                content_type='application/json',
                status=status_code)
        else:
            return HttpResponseRedirect(
                reverse(
                    'geodatabuilder_detail',
                    args=(
                        self.object.id,
                    )))

class GeoDataBuilderUpdate(UpdateView):
    template_name = 'geodatabuilder/geodatabuilder_create.html'
    pk_url_kwarg = 'id'
    form_class = GeoDataBuilderForm
    queryset = GeoDataBuilder.objects.all()
    context_object_name = 'geodatabuilder'

    def get_context_data(self, **kwargs):
        context = super(GeoDataBuilderUpdate, self).get_context_data(**kwargs)
        context['ALLOWED_DOC_TYPES'] = ALLOWED_DOC_TYPES
        return context

    def form_valid(self, form):
        """
        If the form is valid, save the associated model.
        """
        self.object = form.save()
        #register_event(self.request, EventType.EVENT_CHANGE, self.object)
        if self.request.is_ajax():
            success = False
            id = 0
            if self.object.id > 0:
                success = True
                id = self.object.id
            return JsonResponse({
                "success": success,
                "id": id,
                "file_updated": self.object.file_updated
            })
        else:
            return HttpResponseRedirect(
                reverse(
                    'geodatabuilder_detail',
                    args=(
                        self.object.id,
                    )))
        
class GeoDataBuilderDelete(DeleteView):
    template_name = 'geodatabuilder/geodatabuilder_remove.html'
    model = GeoDataBuilder
    pk_url_kwarg = 'id'

    def delete(self, request, *args, **kwargs):
        """
        This does not actually delete the file, only the database record.  But
        that is easy to implement.
        """
        self.object = self.get_object()
        if self.object.owner == self.request.user:
            self.object.delete()
            messages.success(request, 'The Expression is removed.')

        if request.is_ajax():
            response = JSONResponse(
                True, {}, response_content_type(self.request))
            response['Content-Disposition'] = 'inline; filename=files.json'
            return response
        else:
            return HttpResponseRedirect(reverse('geodatabuilder_list'))



class JSONResponse(HttpResponse):

    """JSON response class."""

    def __init__(self,
                 obj='',
                 json_opts=None,
                 content_type="application/json", *args, **kwargs):

        if json_opts is None:
            json_opts = {}
        content = json.dumps(obj, **json_opts)
        super(JSONResponse, self).__init__(
            content, content_type, *args, **kwargs)


def response_content_type(request):
    if "application/json" in request.META['HTTP_ACCEPT']:
        return "application/json"
    else:
        return "text/plain"


class GeoDataBuilderExpressionLayers(APIView): 
    def get(self, request):
        expression = ""
        resp = ""
        success = True
        if request.method == 'GET' and 'expression' in request.GET:
            if (request.GET['expression']):
                expression = request.GET['expression'].replace("'", "")           
                grid = ''
                if (request.GET['grid']):
                    grid = request.GET['grid']
                out = StringIO.StringIO()
                call_command('expressionlayers', expression=expression, grid=grid, stdout=out)
                resp = out.getvalue()
            else :
                success= False                

        return Response(
            {
                "success" : success,
                "resp" : resp
            }
        )




# class GeoDataBuilderExpressionLayers(View):    

#     def post(self, request, *args, **kwargs):
        
#         call_command('expressionlayers', expression=expression, directory=directory)

#         out = {'success': True,
#                 'status': 'ok',
#                 'errors': {}
#                 }
#         return json_response(out)

# @login_required
# def document_remove(request, id, template='documents/document_remove.html'):
#     try:
#         document = _resolve_geodatabuilder(
#             request,
#             docid,
#             'base.delete_resourcebase',
#             _PERMISSION_MSG_DELETE)

#         if request.method == 'GET':
#             return render(request, template, context={
#                 "document": document
#             })

#         if request.method == 'POST':
#             document.delete()

#             #register_event(request, EventType.EVENT_REMOVE, document)
#             return HttpResponseRedirect(reverse("geodatabuilder_list"))
#         else:
#             return HttpResponse(_NOT_ALLOWED, status=403)

#     except PermissionDenied:
#         return HttpResponse(
#             _PERMISSION_MSG_DELETE_ALLOWED,
#             content_type="text/plain",
#             status=401
#         )


    