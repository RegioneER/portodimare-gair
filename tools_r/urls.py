from django.conf.urls import url
from django.views.generic import TemplateView
from django.contrib.auth.decorators import login_required

from . import views

urlpatterns = [
    url(r'^1.8/$', views.tools_r_1_8_list, name='tools_r_1_8_list'),
    url(r'^1.8/create', login_required(views.ToolsR_1_8Create.as_view()), name='tools_r_1_8_create'),
    url(r'^1.8/(?P<id>[^/]*)/$', views.tools_r_1_8_detail, name='tools_r_1_8_detail'),
    url(r'^1.8/remove/(?P<id>[^/]*)/$', login_required(views.ToolsR_1_8Delete.as_view()), name='tools_r_1_8_remove'),

    url(r'^1.11/$', views.tools_r_1_11_list, name='tools_r_1_11_list'),
    url(r'^1.11/create', login_required(views.ToolsR_1_11Create.as_view()), name='tools_r_1_11_create'),
    url(r'^1.11/clone/(?P<id>[^/]*)/$', login_required(views.tools_r_1_11_clone) , name='tools_r_1_11_clone'),
    url(r'^1.11/edit/(?P<id>[^/]*)/$', login_required(views.ToolsR_1_11Update.as_view() ) , name='tools_r_1_11_edit'),
    url(r'^1.11/(?P<id>[^/]*)/$', views.tools_r_1_11_detail, name='tools_r_1_11_detail'),
    url(r'^1.11/remove/(?P<id>[^/]*)/$', login_required(views.ToolsR_1_11Delete.as_view()), name='tools_r_1_11_remove'),

    url(r'^1.12/$', views.tools_r_1_12_list, name='tools_r_1_12_list'),
    url(r'^1.12/create', login_required(views.ToolsR_1_12Create.as_view()), name='tools_r_1_12_create'),
    url(r'^1.12/clone/(?P<id>[^/]*)/$', login_required(views.tools_r_1_12_clone) , name='tools_r_1_12_clone'),
    url(r'^1.12/edit/(?P<id>[^/]*)/$', login_required(views.ToolsR_1_12Update.as_view() ) , name='tools_r_1_12_edit'),
    url(r'^1.12/(?P<id>[^/]*)/$', views.tools_r_1_12_detail, name='tools_r_1_12_detail'),
    url(r'^1.12/remove/(?P<id>[^/]*)/$', login_required(views.ToolsR_1_12Delete.as_view()), name='tools_r_1_12_remove'),
]
 