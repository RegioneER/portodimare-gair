# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.contrib import admin
from base_ext.models import MainCategory, DomainArea, DataPortal, ValidationLevel

# Register your models here.

class DomainAreaAdmin(admin.ModelAdmin):
    model = DomainArea
    list_display = ('identifier', 'description', 'gn_description')
    list_filter = ('identifier','gn_description',)
    search_fields = ('identifier', 'gn_description',)

admin.site.register(MainCategory)
admin.site.register(DomainArea,DomainAreaAdmin)
admin.site.register(DataPortal)
admin.site.register(ValidationLevel)
