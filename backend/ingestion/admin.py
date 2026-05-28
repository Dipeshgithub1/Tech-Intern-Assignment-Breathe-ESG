from django.contrib import admin
from .models import DataSource, RawDataFile


@admin.register(DataSource)
class DataSourceAdmin(admin.ModelAdmin):
    list_display = ['name', 'source_type', 'tenant', 'created_at']
    list_filter = ['source_type']
    search_fields = ['name']


@admin.register(RawDataFile)
class RawDataFileAdmin(admin.ModelAdmin):
    list_display = ['file_name', 'source', 'status', 'uploaded_at']
    list_filter = ['status']
    search_fields = ['file_name']