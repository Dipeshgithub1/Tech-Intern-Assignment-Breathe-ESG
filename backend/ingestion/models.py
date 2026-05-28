from django.db import models
from tenants.models import Tenant
import uuid


class DataSource(models.Model):

    SOURCE_TYPES = [
        ("SAP", "SAP"),
        ("UTILITY", "Utility"),
        ("TRAVEL", "Travel"),
    ]

    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False
    )

    tenant = models.ForeignKey(
        Tenant,
        on_delete=models.CASCADE
    )

    source_type = models.CharField(
        max_length=20,
        choices=SOURCE_TYPES
    )

    name = models.CharField(max_length=255, help_text="Human-readable name for this data source")

    config = models.JSONField(default=dict, blank=True, help_text="Source-specific configuration")

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    def __str__(self):
        return f"{self.name} ({self.source_type})"


class RawDataFile(models.Model):

    STATUS = [
        ("PENDING", "Pending"),
        ("PROCESSED", "Processed"),
        ("FAILED", "Failed"),
    ]

    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False
    )

    source = models.ForeignKey(
        DataSource,
        on_delete=models.CASCADE,
        related_name='files'
    )

    uploaded_file = models.FileField(
        upload_to="uploads/",
        null=True,
        blank=True
    )

    file_name = models.CharField(max_length=255, blank=True)

    status = models.CharField(
        max_length=20,
        choices=STATUS,
        default="PENDING"
    )

    error_message = models.TextField(blank=True)

    uploaded_at = models.DateTimeField(
        auto_now_add=True
    )

    processed_at = models.DateTimeField(null=True, blank=True)