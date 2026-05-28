from django.db import models
from tenants.models import Tenant
from ingestion.models import DataSource
import uuid
from datetime import date as default_date


class NormalizedRecord(models.Model):

    REVIEW_STATUS = [
        ("PENDING", "Pending"),
        ("APPROVED", "Approved"),
        ("REJECTED", "Rejected"),
    ]

    SCOPES = [
        ("SCOPE1", "Scope 1"),
        ("SCOPE2", "Scope 2"),
        ("SCOPE3", "Scope 3"),
    ]

    ACTIVITY_TYPES = [
        ("FUEL", "Fuel Combustion"),
        ("ELECTRICITY", "Electricity Consumption"),
        ("FLIGHT", "Business Flight"),
        ("HOTEL", "Hotel Stay"),
        ("GROUND_TRANSPORT", "Ground Transportation"),
        ("PROCUREMENT", "Procurement/Upstream"),
    ]

    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False
    )

    tenant = models.ForeignKey(
        Tenant,
        on_delete=models.CASCADE,
        related_name='records'
    )

    source = models.ForeignKey(
        DataSource,
        on_delete=models.SET_NULL,
        null=True,
        related_name='records'
    )

    raw_file = models.ForeignKey(
        'ingestion.RawDataFile',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='normalized_records'
    )

    original_row_id = models.CharField(max_length=100, blank=True, help_text="Reference to original row in source")

    activity_type = models.CharField(
        max_length=100,
        choices=ACTIVITY_TYPES
    )

    scope = models.CharField(
        max_length=20,
        choices=SCOPES
    )

    amount = models.FloatField(help_text="Normalized amount in CO2e", null=True, default=0)

    original_amount = models.FloatField(null=True, blank=True, help_text="Original amount before conversion")

    original_unit = models.CharField(
        max_length=50,
        help_text="Original unit (e.g., 'gallons', 'kWh', 'miles')",
        default=''
    )

    normalized_unit = models.CharField(
        max_length=50,
        default="kg CO2e",
        help_text="Normalized unit (kg CO2e)"
    )

    emission_factor = models.FloatField(null=True, blank=True, help_text="Emission factor used for conversion")

    emission_factor_source = models.CharField(max_length=255, blank=True, help_text="Source of emission factor")

    start_date = models.DateField(help_text="Start date of activity period", default=default_date.today)

    end_date = models.DateField(help_text="End date of activity period", default=default_date.today)

    facility_code = models.CharField(max_length=100, blank=True, help_text="Plant/facility identifier")

    facility_name = models.CharField(max_length=255, blank=True)

    description = models.TextField(blank=True)

    suspicious_flag = models.BooleanField(default=False)

    suspicious_reason = models.TextField(blank=True, help_text="Why this record was flagged as suspicious")

    review_status = models.CharField(
        max_length=20,
        choices=REVIEW_STATUS,
        default="PENDING"
    )

    reviewed_by = models.CharField(max_length=100, blank=True)

    reviewed_at = models.DateTimeField(null=True, blank=True)

    source_reference = models.CharField(
        max_length=255,
        help_text="Reference back to source document/system",
        default=''
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    updated_at = models.DateTimeField(
        auto_now=True
    )

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['tenant', 'review_status']),
            models.Index(fields=['tenant', 'start_date']),
            models.Index(fields=['scope', 'activity_type']),
        ]

    def __str__(self):
        return f"{self.activity_type}: {self.amount} {self.normalized_unit} ({self.review_status})"