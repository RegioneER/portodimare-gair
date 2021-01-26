# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.contrib import admin

# Register your models here.

from .models import  CasestudiesModule, CasestudiesCsType, CasestudiesToken #, CasestudiesList


class CasestudiesModuleAdmin(admin.ModelAdmin):
    fields = ('name', 'slug')

class CasestudiesCsTypeAdmin(admin.ModelAdmin):
    fields = ('name', 'slug')

class CasestudiesTokenAdmin(admin.ModelAdmin):
    fields = ('label', 'token', 'schema' , 'is_enabled')
    list_display = ('label', 'token', 'is_enabled')
    list_display_links = ('label', 'token')

"""
class CasestudiesListAdmin(admin.ModelAdmin):
    fields = ('casestudy_api_id', 'casestudy_pdm_id' , 'user')
    list_display = ('casestudy_api_id', 'casestudy_pdm_id', 'user')
    #list_display_links = ('casestudy_api_id')
"""

admin.site.register(CasestudiesToken, CasestudiesTokenAdmin)
admin.site.register(CasestudiesModule, CasestudiesModuleAdmin)
admin.site.register(CasestudiesCsType, CasestudiesCsTypeAdmin)
#admin.site.register(CasestudiesList, CasestudiesListAdmin)


