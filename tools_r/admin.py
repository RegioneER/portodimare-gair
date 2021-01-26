# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.contrib import admin

# Register your models here.

from .models import ToolsR_1_8, ToolsR_1_11, ToolsR_1_12

class ToolsR_1_8Admin(admin.ModelAdmin):
    model = ToolsR_1_8
    list_display = ('label', 'updated','owner','status','output_files','public', )
    list_filter = ('label', 'owner', 'status',)
    search_fields = ('label', 'owner', 'status',)

admin.site.register(ToolsR_1_8, ToolsR_1_8Admin)

class ToolsR_1_11Admin(admin.ModelAdmin):
    model = ToolsR_1_11
    list_display = ('label', 'updated','owner','status','output_files','public', )
    list_filter = ('label', 'owner', 'status',)
    search_fields = ('label', 'owner', 'status',)

admin.site.register(ToolsR_1_11, ToolsR_1_11Admin)

class ToolsR_1_12Admin(admin.ModelAdmin):
    model = ToolsR_1_12
    list_display = ('label', 'updated','owner','status','output_files','public', )
    list_filter = ('label', 'owner', 'status',)
    search_fields = ('label', 'owner', 'status',)

admin.site.register(ToolsR_1_12, ToolsR_1_12Admin)