from django.conf.urls import url
from django.views.generic import TemplateView

# from .views import CasestudiesDetail
from . import views

urlpatterns = [
    url(r'^$', views.casestudies, name='casestudies'),
    url(r'^(?P<id>[^/]*)/$', views.casestudies_detail, name='casestudies_detail'),
    url(r'^create', views.casestudies_create, name='casestudies_create'),
    
]
 