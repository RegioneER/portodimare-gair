from django.conf.urls import url
from django.views.generic import TemplateView
from django.contrib.auth.decorators import login_required

from . import views

urlpatterns = [
    url(r'^/?$', views.geodatabuilder_list, name='geodatabuilder_list'),
    url(r'^detail/(?P<id>[^/]*)/$', views.geodatabuilder_detail, name='geodatabuilder_detail'),
    url(r'^edit/(?P<id>[^/]*)/$', login_required(views.GeoDataBuilderUpdate.as_view()) , name='geodatabuilder_edit'),
    url(r'^clone/(?P<id>[^/]*)/$', login_required(views.geodatabuilder_clone) , name='geodatabuilder_clone'),
    url(r'^create', login_required(views.GeoDataBuilderCreate.as_view()), name='geodatabuilder_create'),
    url(r'^remove/(?P<id>[^/]*)/$', login_required(views.GeoDataBuilderDelete.as_view()), name='geodatabuilder_remove'),
    url(r'^expressionlayers', views.GeoDataBuilderExpressionLayers.as_view(), name='geodatabuilder_expressionlayers'),
    
]
 