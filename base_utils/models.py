from django.db import models
from django.utils.text import slugify
import uuid

# ==========================================
# CUSTOM DYNAMIC WORKFLOW ENGINE
# ==========================================

class WorkflowState(models.Model):
    """
    Our native replacement for django-river.
    Allows Super Admins to dynamically create states (e.g., "Pending", "Shipped")
    from the dashboard without writing code.

    Field shape mirrors django-river's own State model (the `river_state`
    table: label, slug, description, date_created, date_updated). Like
    django-river, states are a universal, shared pool — not scoped to one
    model — so the same "Published" state can back the `status` field on
    Product, Order, or anything else that inherits BaseModel.
    """
    label = models.CharField(max_length=50, unique=True)
    slug = models.SlugField(max_length=60, blank=True, null=True, unique=True)
    description = models.CharField(max_length=200, blank=True, null=True)

    date_created = models.DateTimeField(auto_now_add=True, null=True)
    date_updated = models.DateTimeField(auto_now=True, null=True)

    class Meta:
        db_table = 'azt_workflow_states'

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.label)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.label

# ==========================================
# BASE MODEL
# ==========================================

class BaseModel(models.Model):
    """
    Abstract base model that provides:
    1. A secure, non-sequential UUID as the primary key.
    2. Dynamic workflow states via our custom WorkflowState.
    3. Automatic creation and modification auditing timestamps.
    """
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    # Our custom dynamic status field
    status = models.ForeignKey(
        WorkflowState, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        # This complex related_name prevents Django errors when multiple models inherit BaseModel
        related_name="%(app_label)s_%(class)s_status"
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True