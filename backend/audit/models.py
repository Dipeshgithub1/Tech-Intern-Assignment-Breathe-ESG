from django.db import models
from emissions.models import NormalizedRecord
import uuid


class AuditLog(models.Model):

    CHANGE_TYPES = [
        ("REVIEW", "Review Status Change"),
        ("EDIT", "Field Edit"),
        ("FLAG", "Suspicious Flag"),
        ("CREATE", "Record Created"),
        ("DELETE", "Record Deleted"),
    ]

    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False
    )

    record = models.ForeignKey(
        NormalizedRecord,
        on_delete=models.CASCADE,
        related_name='audit_logs'
    )

    change_type = models.CharField(
        max_length=20,
        choices=CHANGE_TYPES
    )

    old_value = models.JSONField(null=True, blank=True)

    new_value = models.JSONField(null=True, blank=True)

    changed_by = models.CharField(
        max_length=100,
        help_text="Username or identifier of person/system making change"
    )

    changed_at = models.DateTimeField(
        auto_now_add=True
    )

    class Meta:
        ordering = ['-changed_at']
        indexes = [
            models.Index(fields=['record', 'changed_at']),
        ]

    def __str__(self):
        return f"{self.change_type} on {self.record.id} by {self.changed_by}"