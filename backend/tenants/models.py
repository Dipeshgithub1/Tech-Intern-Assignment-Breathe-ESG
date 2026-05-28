
# Create your models here.
from django.db import models
import uuid


class Tenant(models.Model):
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False
    )

    company_name = models.CharField(max_length=255)

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    def __str__(self):
        return self.company_name