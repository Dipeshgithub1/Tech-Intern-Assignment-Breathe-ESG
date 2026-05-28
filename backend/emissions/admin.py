from django.contrib import admin
from .models import NormalizedRecord


@admin.register(NormalizedRecord)
class NormalizedRecordAdmin(admin.ModelAdmin):
    list_display = ['activity_type', 'scope', 'amount', 'review_status', 'suspicious_flag', 'created_at']
    list_filter = ['scope', 'activity_type', 'review_status', 'suspicious_flag']
    search_fields = ['facility_name', 'facility_code', 'source_reference']