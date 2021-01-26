# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.shortcuts import render
from django.contrib.messages import get_messages

from django.views.generic import View, DetailView
from django.views.generic.edit import UpdateView, CreateView, DeleteView
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, HttpResponseRedirect, Http404, JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.core.management import call_command
from django.core.urlresolvers import reverse
from django.db.models import Q

# Create your views here.
from rest_framework.response import Response

from .forms import ToolsR_1_8Form, ToolsR_1_11Form, ToolsR_1_12Form
from .models import ToolsR_1_8, ToolsR_1_11, ToolsR_1_12

from django.conf import settings

from geonode.utils import resolve_object
from django.utils.translation import ugettext as _

import json, random, string, StringIO, shutil, os, datetime, tempfile, re

from casestudies.models import   CasestudiesCsType

from django.core.paginator import Paginator, InvalidPage


# Create your views here.
import logging

logger = logging.getLogger("geonode.documents.views")

ALLOWED_DOC_TYPES = settings.ALLOWED_DOCUMENT_TYPES

_NOT_ALLOWED = _("Not allowed")
_PERMISSION_MSG_DELETE = _("You are not permitted to delete this Tools R")
_PERMISSION_MSG_DELETE_ALLOWED = _("You are not allowed to delete this Tools R")
_PERMISSION_MSG_GENERIC = _("You do not have permissions for this Tools R.")
_PERMISSION_MSG_MODIFY = _("You are not permitted to modify this Tools R")
_PERMISSION_MSG_METADATA = _(
    "You are not permitted to modify this Tools R's metadata")
_PERMISSION_MSG_VIEW = _("You are not permitted to view this Tools R")

def randomString(stringLength=6):
    """Generate a random string of fixed length """
    letters = string.ascii_lowercase
    return ''.join(random.choice(letters) for i in range(stringLength))

def _resolve_tools_r(request, id, permission='base.change_resourcebase',
                      msg=_PERMISSION_MSG_GENERIC, **kwargs):
    '''
    Resolve the Tools R by the provided primary key and check the optional permission.
    '''
    return resolve_object(request, ToolsR, {'id': id},
                          permission=permission, permission_msg=msg, **kwargs)


def get_current_user(request):
    current_user = request.user
    return current_user



def tool_r_list(request , id_tool, ToolsR):

    m = ""
    messages = get_messages(request)
    for message in messages:
        m = str(m) +  str(message) + str("<br />")
    
    
    query_param = {}

    _limit = settings.CLIENT_RESULTS_LIMIT
    _offset = "0"
    _owner = ""
    _type_obj = {}
    _type = ""
    _label = ""
    _created = ""
    _order_by = "-updated"
    _page = "1"
    _owner_obj = {}

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
                _owner_obj = get_user_model().objects.get( username= _owner)
                query_param["owner"] = _owner_obj.id
    
    if request.method == 'GET' and 'label' in request.GET:
        if (request.GET['label']):
            _label = request.GET['label']
            query_param["label__icontains"] = _label

    if request.method == 'GET' and 'order_by' in request.GET:
        if (request.GET['order_by']):
            _order_by = request.GET['order_by']
    
    
    if request.method == 'GET' and 'cstype' in request.GET:
        if (request.GET['cstype']):
            _type_slug = request.GET['cstype']
            if len(_type_slug) > 0:
                _type_obj = CasestudiesCsType.objects.get(slug=_type_slug)
                if _type_obj:
                    query_param["type"] = _type_obj.id
            
    

    items = ToolsR.objects.filter( **query_param ).order_by(_order_by)
    
    paginator = Paginator(items, _limit)

    resp_items = []
    for item in items:    
        
        resp_item = item
        resp_item.full_url = reverse(
            'tools_r_1_' + id_tool + '_detail',
            args=(
                item.id,
            ))
        
        if item.public == True :
            resp_items.append(resp_item)
        else :
            if request.user.is_authenticated() and item.owner == request.user:
                resp_items.append(resp_item)

        

    

    tool_r_user = ToolsR.objects.order_by("owner").distinct('owner')
    
    owners = []
    owners_sort = []
    for g in tool_r_user:
        user_query_param = {}
        user_query_param["owner"] = g.owner
        user_query_param["public"] = True
        if request.user.is_authenticated() and g.owner == request.user: 
            user_query_param.pop('public')

        user = {}
        user["owner"] = g.owner
        user["full_name"] = g.owner.get_full_name() or g.owner.get_username()
        user["username"] = g.owner.get_username()
        user["data_value"] = user["username"]
        user["name"] = user["full_name"]

        user["tot"] = ToolsR.objects.filter( **user_query_param ).count()
        
        if user["tot"] > 0:
            owners.append( user )
    
    # owners_sort = owners.sort(key=lambda x: x["full_name"])
    owners_sort = sorted(owners , key = lambda x: x["full_name"] )

    
    

    next_page = 0
    previous_page = 0
    total_count = 0
    num_pages = paginator.num_pages
    # resp_item = []
    # current_page = int(_offset or 0) / int(_limit, 0) + 1
    current_page = _page
    
    try:
        page = paginator.page(current_page)
        # previous_page_number = page.previous_page_number()
        # next_page_number = page.next_page_number()
        
        resp_item = page.object_list
    
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
    
    total_count = len(resp_items)


    cs_type = []
    resp_cs_type = []
    cs_type = CasestudiesCsType.objects.all()
    for t in cs_type:
        resp_t = {}
        resp_t_arr = []
        type_query_param = {}
        type_query_param["type"] = t.id
        resp_t["slug"] = t.slug
        resp_t["data_value"] = resp_t["slug"]
        resp_t["name"] = t.name
        count_tot = 0
        tot = ToolsR.objects.filter( **type_query_param )
        for i in tot:
            if i.public == True :
                resp_t_arr.append( resp_t )
            else :
                if request.user.is_authenticated() and i.owner == request.user:
                    resp_t_arr.append( resp_t )
        
        resp_t["tot"] = len(resp_t_arr)
        
        if resp_t["tot"] > 0:
            resp_cs_type.append( resp_t )

        # resp_t["tot"] = ToolsR.objects.filter( **type_query_param ).count()
        

    return render(
        request,
        "tools_r/tools_r_1_" + id_tool + "_list.html",
        {
            "type": resp_cs_type,
            "current_page": current_page,
            "num_pages": num_pages,
            "next": next_page,
            "previous": previous_page,
            "total_count": total_count,
            "items" : resp_items,
            "tool_r_user" : tool_r_user,
            "tool_r_list_url": reverse(
                'tools_r_1_' + id_tool + '_list'
            ),
            "owners" : owners_sort,
            "cta_create_new": reverse(
                'tools_r_1_' + id_tool + '_create'
            )
        }
    )



def tools_r_1_8_list(request):
    """This view shows the list of all registered services"""
    return tool_r_list(request, '8', ToolsR_1_8 )

def tools_r_1_8_detail(request, id):

    tools_r = get_object_or_404(ToolsR_1_8, id=id)

    strtoolr = randomString()
    if (tools_r.output_files):
        strtoolr = os.path.basename(os.path.normpath(tools_r.output_files))
  
    status = request.POST.get('status', False)
    if (status == False):
        status = tools_r.status

    public = tools_r.public
    public_check = request.POST.get('public', False)
    if public_check == "on":
        public = True
    
    response = ""
    if not tools_r.output_files or status == "create" or status == "update":

        tr = ToolsR_1_8.objects.filter(id=id).update(updated=datetime.datetime.now(), output_files=settings.R_URL_OUTPUT+"1.8/"+strtoolr+"/", status="pending", public=public)
        tools_r.updated = datetime.datetime.now()
        tools_r.public = public
        tools_r.status = "pending" 

        out = StringIO.StringIO()
        try:
            call_command('runtool_r_1_8', 
                directory=settings.R_DIR_INPUT+"1.8/",
                output=settings.R_DIR_OUTPUT+"1.8/",
                criteria=tools_r.input_criteria,
                strtoolr=strtoolr, 
                id_tool=id,
                stdout=out)
            response = out.getvalue()
            tools_r.status = "completed" 
        except:
            response = "fail, R Server not working."
            tr = ToolsR_1_11.objects.filter(id=id).update(status=status)
            tools_r.status = status 
           
    if (tools_r.status == "pending"):
        response = "The MSF tool is now running. Please come back in about 40/60 minutes to check the output  results in the MSF module case studies page"
    
    out_files = None
    result = re.search('\[(.*)\]', response)
    if (result):
        out_files = result.group(1)
    else:
        out_files = strtoolr

    if tools_r.type == None:
        tools_r.type = settings.DEFAULT_CASESTUDY_TYPE_ID

    return render(request, "tools_r/tools_r_1_8_detail.html", {
        "tools_r": tools_r,
        "type_value": CasestudiesCsType.objects.get(id=tools_r.type),
        "resp_command": {
            "check": (response.find('fail') == -1 and tools_r.status.find('pending') == -1),
            "response": response,
            "output_files": settings.R_URL_OUTPUT+"1.8/"+out_files+"/"
        },
        "user": get_current_user(request)
    })


class ToolsR_1_8Create(CreateView):
    template_name = 'tools_r/tools_r_1_8_create.html'
    form_class = ToolsR_1_8Form

    # def get_initial(self, form):
    #     #form = self.get_form()
    #     # type_value = 2
    #     # if form.type > 0:
    #     #     type_value = form.type
    #     return {
    #         "type" : self.get_context_data(form=form)
    #     }


    def get_context_data(self, **kwargs):
        context = super(ToolsR_1_8Create, self).get_context_data(**kwargs)
        context['ALLOWED_DOC_TYPES'] = ALLOWED_DOC_TYPES
        context['type'] = CasestudiesCsType.objects.all()
        context['form'] = self.get_form()
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
           # form.input_layers = None
            return self.render_to_response(self.get_context_data(form=form))

    def form_valid(self, form):
        """
        If the form is valid, save the associated model.
        """
        self.object = form.save(commit=False)
        self.object.owner = self.request.user
        self.object.status = "create"
        self.object.save()
        
        out = {'success': False}

        if self.request.GET.get('no__redirect', False):
            out['success'] = True
            out['url'] = reverse(
                'tools_r_1_8_detail',
                args=(
                    self.object.id,
                ))
            return HttpResponse(
                json.dumps(out),
                content_type='application/json',
                status=200)
        else:
            return HttpResponseRedirect(
                reverse(
                    'tools_r_1_8_detail',
                    args=(
                        self.object.id,
                    )))


class ToolsR_1_8Delete(DeleteView):
    template_name = 'tools_r/tools_r_1_8_remove.html'
    model = ToolsR_1_8
    pk_url_kwarg = 'id'
    context_object_name = 'tools_r'

    def delete(self, request, *args, **kwargs):
        """
        This does not actually delete the file, only the database record.  But
        that is easy to implement.
        """
        self.object = self.get_object()
        if self.object.owner == self.request.user or self.request.user.is_superuser:
            output_files = os.path.basename(os.path.normpath(self.object.output_files))
            self.object.delete()
            # elimino la cartella con i files...
            shutil.rmtree(settings.R_DIR_OUTPUT+"1.8/"+output_files+'/')
            
        if request.is_ajax():
            response = JSONResponse(
                True, {}, response_content_type(self.request))
            response['Content-Disposition'] = 'inline; filename=files.json'
            return response
        else:
            return HttpResponseRedirect(reverse('tools_r_1_8_list'))










def tools_r_1_11_clone(request, id):
    """This view shows the list of all registered services"""
    
    c = get_object_or_404(ToolsR_1_11, id=id)
    c.id = None
    
    _label = c.label
    if 'label' in request.POST:
        if (request.POST['label']):
            _label = request.POST['label']
    c.label = _label    

    c.output_files = ''
    c.status = "clone"
    c.updated = datetime.datetime.now()
    c.save()

    return HttpResponseRedirect(
        reverse(
            'tools_r_1_11_detail',
            args=(c.id,)))


def tools_r_1_11_list(request):
    """This view shows the list of all registered services"""
    return tool_r_list(request, '11' , ToolsR_1_11)

def tools_r_1_11_detail(request, id):

    tools_r = get_object_or_404(ToolsR_1_11, id=id)
    
    pairwise_matrix = json.dumps(tools_r.pairwise_matrix)
    fishing_gear = json.dumps(tools_r.fishing_gear)

    strtoolr = randomString()
    if (tools_r.output_files):
        strtoolr = os.path.basename(os.path.normpath(tools_r.output_files))
  
    # crea la directory di output se inesistente..
    dir_output = settings.R_DIR_OUTPUT+"1.11/"+strtoolr+'/'
    if not os.path.exists(dir_output):
        os.makedirs(dir_output)

    status = request.POST.get('status', False)
    if (status == False):
        status = tools_r.status

    if (status == "create"):
        
        fieldnames = ("bathymetry", "coast_dist", "legislation", "trawl_fleet", "seine_fleet", "marine_traffic", "chlorophyl")
        pairwise_matrix = json.loads(tools_r.pairwise_matrix)

        pairwise_matrix_csv = ','+','.join(map(str, fieldnames))+"\n"

        for row in fieldnames:
            row_str = ""
            row_str += row
            for col in fieldnames:
                row_str += ','+pairwise_matrix[row][col]
            pairwise_matrix_csv += row_str+"\n"
        
        f = open(dir_output+'pairwise_matrix.csv','w')
        f.write(pairwise_matrix_csv) #Give your csv text here.
        f.close()


        nameField = ("Longitude", "Latitude", "GT")
        fishing_gear = json.loads(tools_r.fishing_gear)
       
        fishing_gear_csv = ','.join(map(str, nameField))+"\n"
       
        for elem in fishing_gear:
            row_obj = fishing_gear[elem]
            row_str = ""
            i=0
            for value in nameField:
                print value
                if i > 0:
                    row_str += ','+row_obj[value]
                else:
                    row_str += row_obj[value]
                i=i+1
            fishing_gear_csv += row_str+"\n"
        
        f = open(dir_output+'Fishing_Gear.csv','w')
        f.write(fishing_gear_csv) #Give your csv text here.
        f.close()

    public = tools_r.public
    public_check = request.POST.get('public', False)
    if public_check == "on":
        public = True
    
    if tools_r.type == None:
        tools_r.type = settings.DEFAULT_CASESTUDY_TYPE_ID

    response = ""
    if (not tools_r.output_files and status != "clone") or status == "create" or status == "update":
        
        tr = ToolsR_1_11.objects.filter(id=id).update(updated=datetime.datetime.now(), output_files=settings.R_URL_OUTPUT+"1.11/"+strtoolr+"/", status="pending", public=public)
        tools_r.updated = datetime.datetime.now()
        tools_r.public = public
        tools_r.status = "pending" 
    
        out = StringIO.StringIO()
        try:
            call_command('runtool_r_1_11', 
                directory=settings.R_DIR_INPUT+"1.11/",
                output=settings.R_DIR_OUTPUT+"1.11/",
                criteria=tools_r.input_criteria,
                strtoolr=strtoolr,
                id_tool=id,
                stdout=out)
            response = out.getvalue()
            tools_r.status = "completed" 
        except:
            response = "fail: R Server not working."
            tr = ToolsR_1_11.objects.filter(id=id).update(status=status)
            tools_r.status = status 

    if (tools_r.status == "pending"):
        response = "The SSF tool is now running. Please come back in about 40/60 minutes to check the output  results in the MSF module case studies page "
    
    if (tools_r.status == "clone"):
        response = "The SSF tool has been cloned. Run tool."

    out_files = None
    result = re.search('\[(.*)\]', response)
    if (result):
        out_files = result.group(1)
    else:
        out_files = strtoolr

    return render(request, "tools_r/tools_r_1_11_detail.html", {
        "tools_r": tools_r,
        "type_value": CasestudiesCsType.objects.get(id=tools_r.type),
        "resp_command": {
            "check": (response.find('fail') == -1 and tools_r.status.find('pending') == -1 and tools_r.status.find('clone') == -1),
            "response": response,
            "output_files": settings.R_URL_OUTPUT+"1.11/"+out_files+"/"
        },
        "user": get_current_user(request)
    })


class ToolsR_1_11Create(CreateView):
    template_name = 'tools_r/tools_r_1_11_create.html'
    form_class = ToolsR_1_11Form

    def get_initial(self):

        pairwise_matrix = {}
        with open(settings.R_DIR_INPUT+"1.11/pairwise_matrix.csv", 'r') as csvfile:
            fieldnames = ("bathymetry", "coast_dist", "legislation", "trawl_fleet", "seine_fleet", "marine_traffic", "chlorophyl")
            x=0
            for row in csvfile:
                if x > 0:
                    list_row = row.split(',')
                    name_row = list_row[0] 
                    del list_row[0] 
                    y = 0
                    json_temp={}
                    for value in list_row:
                        json_temp[fieldnames[y]] = value
                        y=y+1
                    pairwise_matrix[name_row] = json_temp
                        
                x=x+1

        nameField = ("Longitude", "Latitude", "GT")
        fishing_gear = {}
        with open(settings.R_DIR_INPUT+"1.11/Fishing_Gear.csv", 'r') as csvfile:
            x=0
            for row in csvfile:
                if x > 0:
                    list_row = row.split(',')
                    y = 0
                    json_temp={}
                    for value in list_row:
                        json_temp[nameField[y]] = value.replace("\r\n","")
                        y=y+1
                        fishing_gear[x-1] = json_temp
                x=x+1

        return {
            'pairwise_matrix': json.dumps(pairwise_matrix),
            'fishing_gear': json.dumps(fishing_gear)
        }

    def get_context_data(self, **kwargs):
        context = super(ToolsR_1_11Create, self).get_context_data(**kwargs)
        context['ALLOWED_DOC_TYPES'] = ALLOWED_DOC_TYPES
        context['type'] = CasestudiesCsType.objects.all()
        context['form'] = self.get_form()
     
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
           # form.input_layers = None
            return self.render_to_response(self.get_context_data(form=form))

    def form_valid(self, form):
        """
        If the form is valid, save the associated model.
        """
        self.object = form.save(commit=False)
        self.object.owner = self.request.user
        self.object.status = "create"
        self.object.save()
        
        out = {'success': False}

        if self.request.GET.get('no__redirect', False):
            out['success'] = True
            out['url'] = reverse(
               'tools_r_1_11_detail',
                args=(
                    self.object.id,
                ))
            return HttpResponse(
                json.dumps(out),
                content_type='application/json',
                status=200)
        else:
            return HttpResponseRedirect(
                reverse(
                    'tools_r_1_11_detail',
                    args=(
                        self.object.id,
                    )))


class ToolsR_1_11Update(UpdateView):
    template_name = 'tools_r/tools_r_1_11_create.html'
    pk_url_kwarg = 'id'
    form_class = ToolsR_1_11Form
    queryset = ToolsR_1_11.objects.all()
    context_object_name = 'form'

    def get_context_data(self, **kwargs):
        context = super(ToolsR_1_11Update, self).get_context_data(**kwargs)
        context['ALLOWED_DOC_TYPES'] = ALLOWED_DOC_TYPES
        context['tool_r'] = self.get_object()
        context["type"] = CasestudiesCsType.objects.all()

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
           # form.input_layers = None
            return self.render_to_response(self.get_context_data(form=form))

    def form_valid(self, form):
        """
        If the form is valid, save the associated model.
        """
        # self.object = form.save(commit=False)
        # self.object.owner = self.request.user
        # self.object.status = "create"
        # self.object.save()

        self.object.status = "edit"
        self.object = form.save()
        
        out = {'success': False}

        if self.request.GET.get('no__redirect', False):
            out['success'] = True
            out['url'] = reverse(
               'tools_r_1_11_detail',
                args=(
                    self.object.id,
                ))
            return HttpResponse(
                json.dumps(out),
                content_type='application/json',
                status=200)
        else:
            return HttpResponseRedirect(
                reverse(
                    'tools_r_1_11_detail',
                    args=(
                        self.object.id,
                    )))


# def tools_r_1_11_update(request, id):
    
#     form_class = ToolsR_1_11Form

#     tools_r = get_object_or_404(ToolsR_1_11, id=id)

#     pairwise_matrix = json.dumps(tools_r.pairwise_matrix)
#     fishing_gear = json.dumps(tools_r.fishing_gear)

#     return render(request, "tools_r/tools_r_1_11_create.html", {
#         "tools_r": tools_r,
#         "user": get_current_user(request),
#         "form": form_class,
#         "pairwise_matrix": pairwise_matrix,
#         "fishing_gear": fishing_gear
#     })


class ToolsR_1_11Delete(DeleteView):
    template_name = 'tools_r/tools_r_1_11_remove.html'
    model = ToolsR_1_11
    pk_url_kwarg = 'id'
    context_object_name = 'tools_r'

    def delete(self, request, *args, **kwargs):
        """
        This does not actually delete the file, only the database record.  But
        that is easy to implement.
        """
        self.object = self.get_object()
        if self.object.owner == self.request.user or self.request.user.is_superuser:
            output_files = os.path.basename(os.path.normpath(self.object.output_files))
            self.object.delete()
            # elimino la cartella con i files...
            if (self.object.output_files):
                shutil.rmtree(settings.R_DIR_OUTPUT+"1.11/"+output_files+'/')
            
        if request.is_ajax():
            response = JSONResponse(
                True, {}, response_content_type(self.request))
            response['Content-Disposition'] = 'inline; filename=files.json'
            return response
        else:
            return HttpResponseRedirect(reverse('tools_r_1_11_list'))










def tools_r_1_12_clone(request, id):
    """This view shows the list of all registered services"""
    
    c = get_object_or_404(ToolsR_1_12, id=id)
    c.id = None
    
    _label = c.label
    if 'label' in request.POST:
        if (request.POST['label']):
            _label = request.POST['label']
    c.label = _label   

    c.output_files = ''
    c.status = "clone"
    c.updated = datetime.datetime.now()
    c.save()

    return HttpResponseRedirect(
        reverse(
            'tools_r_1_12_detail',
            args=(c.id,)))


def tools_r_1_12_list(request):
    """This view shows the list of all registered services"""
    return tool_r_list(request, '12' , ToolsR_1_12)
    

def tools_r_1_12_detail(request, id):

    tools_r = get_object_or_404(ToolsR_1_12, id=id)

    pairwise_matrix_ps = json.dumps(tools_r.pairwise_matrix_ps)
    pairwise_matrix_tr = json.dumps(tools_r.pairwise_matrix_tr)
    fishing_gear_ps = json.dumps(tools_r.fishing_gear_ps)
    fishing_gear_tr1224 = json.dumps(tools_r.fishing_gear_tr1224)
    fishing_gear_tr2440 = json.dumps(tools_r.fishing_gear_tr2440)

    strtoolr = randomString()
    if (tools_r.output_files):
        strtoolr = os.path.basename(os.path.normpath(tools_r.output_files))
  
    # crea la directory di output se inesistente..
    dir_output = settings.R_DIR_OUTPUT+"1.12/"+strtoolr+'/'
    if not os.path.exists(dir_output):
        os.makedirs(dir_output)

    status = request.POST.get('status', False)
    if (status == False):
        status = tools_r.status

    if (status == "create"):
        
        fieldnames_ps = ("bathymetry", "coast_dist", "legislation_PS", "chlorophyl")
        pairwise_matrix_ps = json.loads(tools_r.pairwise_matrix_ps)
        pairwise_matrix_ps_csv = ','+','.join(map(str, fieldnames_ps))+"\n"
        for row in fieldnames_ps:
            row_str = ""
            row_str += row
            for col in fieldnames_ps:
                row_str += ','+pairwise_matrix_ps[row][col]
            pairwise_matrix_ps_csv += row_str+"\n"   
        f = open(dir_output+'pairwise_matrix_PS.csv','w')
        f.write(pairwise_matrix_ps_csv) #Give your csv text here.
        f.close()

        fieldnames_tr = ("bathymetry", "coast_dist", "legislation_TR", "chlorophyl")
        pairwise_matrix_tr = json.loads(tools_r.pairwise_matrix_tr)
        pairwise_matrix_tr_csv = ','+','.join(map(str, fieldnames_tr))+"\n"
        for row in fieldnames_tr:
            row_str = ""
            row_str += row
            for col in fieldnames_tr:
                row_str += ','+pairwise_matrix_tr[row][col]
            pairwise_matrix_tr_csv += row_str+"\n"   
        f = open(dir_output+'pairwise_matrix_TR.csv','w')
        f.write(pairwise_matrix_tr_csv) #Give your csv text here.
        f.close()

        nameField = ("longitude", "latitude", "gtl")
        
        fishing_gear_ps = json.loads(tools_r.fishing_gear_ps)
        fishing_gear_ps_csv = ','.join(map(str, nameField))+"\n"
        for elem in fishing_gear_ps:
            row_obj = fishing_gear_ps[elem]
            row_str = ""
            i=0
            for value in nameField:
                print value
                if i > 0:
                    row_str += ','+row_obj[value]
                else:
                    row_str += row_obj[value]
                i=i+1
            fishing_gear_ps_csv += row_str+"\n"
        f = open(dir_output+'Fishing_Gear_PS.csv','w')
        f.write(fishing_gear_ps_csv) #Give your csv text here.
        f.close()

        fishing_gear_tr1224 = json.loads(tools_r.fishing_gear_tr1224)
        fishing_gear_tr1224_csv = ','.join(map(str, nameField))+"\n"
        for elem in fishing_gear_tr1224:
            row_obj = fishing_gear_tr1224[elem]
            row_str = ""
            i=0
            for value in nameField:
                print value
                if i > 0:
                    row_str += ','+row_obj[value]
                else:
                    row_str += row_obj[value]
                i=i+1
            fishing_gear_tr1224_csv += row_str+"\n"
        f = open(dir_output+'Fishing_Gear_TR1224.csv','w')
        f.write(fishing_gear_tr1224_csv) #Give your csv text here.
        f.close()

        fishing_gear_tr2440 = json.loads(tools_r.fishing_gear_tr2440)
        fishing_gear_tr2440_csv = ','.join(map(str, nameField))+"\n"
        for elem in fishing_gear_tr2440:
            row_obj = fishing_gear_tr2440[elem]
            row_str = ""
            i=0
            for value in nameField:
                print value
                if i > 0:
                    row_str += ','+row_obj[value]
                else:
                    row_str += row_obj[value]
                i=i+1
            fishing_gear_tr2440_csv += row_str+"\n"
        f = open(dir_output+'Fishing_Gear_TR2440.csv','w')
        f.write(fishing_gear_tr2440_csv) #Give your csv text here.
        f.close()

    public = tools_r.public
    public_check = request.POST.get('public', False)
    if public_check == "on":
        public = True
    
    response = ""
    if (not tools_r.output_files and status != "clone") or status == "create" or status == "update":
        
        tr = ToolsR_1_12.objects.filter(id=id).update(updated=datetime.datetime.now(), output_files=settings.R_URL_OUTPUT+"1.12/"+strtoolr+"/", status="pending", public=public)
        tools_r.updated = datetime.datetime.now()
        tools_r.public = public
        tools_r.status = "pending" 
    
        out = StringIO.StringIO()
        try:
            call_command('runtool_r_1_12', 
                directory=settings.R_DIR_INPUT+"1.12/",
                output=settings.R_DIR_OUTPUT+"1.12/",
                criteria=tools_r.input_criteria,
                strtoolr=strtoolr,
                id_tool=id,
                stdout=out)
            response = out.getvalue()
            tools_r.status = "completed" 
        except:
            response = "fail: R Server not working."
            tr = ToolsR_1_12.objects.filter(id=id).update(status=status)
            tools_r.status = status 

    if (tools_r.status == "pending"):
        response = "The MSF tool is now running. Please come back in about 40/60 minutes to check the output  results in the MSF module case studies page "

    if (tools_r.status == "clone"):
        response = "The MSF tool has been cloned. Run tool."

    out_files = None
    result = re.search('\[(.*)\]', response)
    if (result):
        out_files = result.group(1)
    else:
        out_files = strtoolr
    
    if tools_r.type == None:
        tools_r.type = settings.DEFAULT_CASESTUDY_TYPE_ID


    return render(request, "tools_r/tools_r_1_12_detail.html", {
        "tools_r": tools_r,
        "type_value": CasestudiesCsType.objects.get(id=tools_r.type),
        "resp_command": {
            "check": (response.find('fail') == -1 and tools_r.status.find('pending') == -1 and tools_r.status.find('clone') == -1),
            "response": response,
            "output_files": settings.R_URL_OUTPUT+"1.12/"+out_files+"/"
        },
        "user": get_current_user(request)
    })

class ToolsR_1_12Create(CreateView):
    template_name = 'tools_r/tools_r_1_12_create.html'
    form_class = ToolsR_1_12Form

    def get_initial(self):

        pairwise_matrix_ps = {}
        with open(settings.R_DIR_INPUT+"1.12/pairwise_matrix_PS.csv", 'r') as csvfile:
            fieldnames = ("bathymetry", "coast_dist", "legislation_PS", "chlorophyl")
            x=0
            for row in csvfile:
                if x > 0:
                    list_row = row.split(',')
                    name_row = list_row[0] 
                    del list_row[0] 
                    y = 0
                    json_temp={}
                    for value in list_row:
                        json_temp[fieldnames[y]] = value
                        y=y+1
                    pairwise_matrix_ps[name_row] = json_temp
                        
                x=x+1
        
        pairwise_matrix_tr = {}
        with open(settings.R_DIR_INPUT+"1.12/pairwise_matrix_TR.csv", 'r') as csvfile:
            fieldnames = ("bathymetry", "coast_dist", "legislation_TR", "chlorophyl")
            x=0
            for row in csvfile:
                if x > 0:
                    list_row = row.split(',')
                    name_row = list_row[0] 
                    del list_row[0] 
                    y = 0
                    json_temp={}
                    for value in list_row:
                        json_temp[fieldnames[y]] = value
                        y=y+1
                    pairwise_matrix_tr[name_row] = json_temp
                        
                x=x+1

        nameField = ("longitude", "latitude", "gtl")
        fishing_gear_ps = {}
        with open(settings.R_DIR_INPUT+"1.12/Fishing_Gear_PS.csv", 'r') as csvfile:
            x=0
            for row in csvfile:
                if x > 0:
                    list_row = row.split(',')
                    y = 0
                    json_temp={}
                    for value in list_row:
                        json_temp[nameField[y]] = value.replace("\r\n","")
                        y=y+1
                        fishing_gear_ps[x-1] = json_temp
                x=x+1

        fishing_gear_tr1224 = {}
        with open(settings.R_DIR_INPUT+"1.12/Fishing_Gear_TR1224.csv", 'r') as csvfile:
            x=0
            for row in csvfile:
                if x > 0:
                    list_row = row.split(',')
                    y = 0
                    json_temp={}
                    for value in list_row:
                        json_temp[nameField[y]] = value.replace("\r\n","")
                        y=y+1
                        fishing_gear_tr1224[x-1] = json_temp
                x=x+1

        fishing_gear_tr2440 = {}
        with open(settings.R_DIR_INPUT+"1.12/Fishing_Gear_TR2440.csv", 'r') as csvfile:
            x=0
            for row in csvfile:
                if x > 0:
                    list_row = row.split(',')
                    y = 0
                    json_temp={}
                    for value in list_row:
                        json_temp[nameField[y]] = value.replace("\r\n","")
                        y=y+1
                        fishing_gear_tr2440[x-1] = json_temp
                x=x+1

        return {
            'pairwise_matrix_ps': json.dumps(pairwise_matrix_ps),
            'pairwise_matrix_tr': json.dumps(pairwise_matrix_tr),
            'fishing_gear_ps': json.dumps(fishing_gear_ps),
            'fishing_gear_tr1224': json.dumps(fishing_gear_tr1224),
            'fishing_gear_tr2440': json.dumps(fishing_gear_tr2440)
        }

    def get_context_data(self, **kwargs):
        context = super(ToolsR_1_12Create, self).get_context_data(**kwargs)
        context['ALLOWED_DOC_TYPES'] = ALLOWED_DOC_TYPES
        context['type'] = CasestudiesCsType.objects.all()
        context['form'] = self.get_form()
     
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
           # form.input_layers = None
            return self.render_to_response(self.get_context_data(form=form))

    def form_valid(self, form):
        """
        If the form is valid, save the associated model.
        """
        self.object = form.save(commit=False)
        self.object.owner = self.request.user
        self.object.status = "create"
        self.object.save()
        
        out = {'success': False}

        if self.request.GET.get('no__redirect', False):
            out['success'] = True
            out['url'] = reverse(
               'tools_r_1_12_detail',
                args=(
                    self.object.id,
                ))
            return HttpResponse(
                json.dumps(out),
                content_type='application/json',
                status=200)
        else:
            return HttpResponseRedirect(
                reverse(
                    'tools_r_1_12_detail',
                    args=(
                        self.object.id,
                    )))

class ToolsR_1_12Update(UpdateView):
    template_name = 'tools_r/tools_r_1_12_create.html'
    pk_url_kwarg = 'id'
    form_class = ToolsR_1_12Form
    queryset = ToolsR_1_12.objects.all()
    context_object_name = 'form'

    def get_context_data(self, **kwargs):
        context = super(ToolsR_1_12Update, self).get_context_data(**kwargs)
        context['ALLOWED_DOC_TYPES'] = ALLOWED_DOC_TYPES
        context['tool_r'] = self.get_object()
        context["type"] = CasestudiesCsType.objects.all()

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
           # form.input_layers = None
            return self.render_to_response(self.get_context_data(form=form))

    def form_valid(self, form):
        """
        If the form is valid, save the associated model.
        """
        # self.object = form.save(commit=False)
        # self.object.owner = self.request.user
        # self.object.status = "create"
        # self.object.save()

        self.object.status = "edit"
        self.object = form.save()
        
        out = {'success': False}

        if self.request.GET.get('no__redirect', False):
            out['success'] = True
            out['url'] = reverse(
               'tools_r_1_12_detail',
                args=(
                    self.object.id,
                ))
            return HttpResponse(
                json.dumps(out),
                content_type='application/json',
                status=200)
        else:
            return HttpResponseRedirect(
                reverse(
                    'tools_r_1_12_detail',
                    args=(
                        self.object.id,
                    )))

class ToolsR_1_12Delete(DeleteView):
    template_name = 'tools_r/tools_r_1_12_remove.html'
    model = ToolsR_1_12
    pk_url_kwarg = 'id'
    context_object_name = 'tools_r'

    def delete(self, request, *args, **kwargs):
        """
        This does not actually delete the file, only the database record.  But
        that is easy to implement.
        """
        self.object = self.get_object()
        if self.object.owner == self.request.user or self.request.user.is_superuser:
            output_files = os.path.basename(os.path.normpath(self.object.output_files))
            self.object.delete()
            # elimino la cartella con i files...
            if (self.object.output_files):
                shutil.rmtree(settings.R_DIR_OUTPUT+"1.12/"+output_files+'/')
            
        if request.is_ajax():
            response = JSONResponse(
                True, {}, response_content_type(self.request))
            response['Content-Disposition'] = 'inline; filename=files.json'
            return response
        else:
            return HttpResponseRedirect(reverse('tools_r_1_12_list'))








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