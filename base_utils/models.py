from django.db import models
import uuid

# ==========================================
# CUSTOM DYNAMIC WORKFLOW ENGINE
# ==========================================

class WorkflowState(models.Model):
    """
    Our native replacement for django-river. 
    Allows Super Admins to dynamically create states (e.g., "Pending", "Shipped") 
    from the dashboard without writing code.
    """
    name = models.CharField(max_length=100)
    # To know which model this state belongs to (e.g., "Product" or "Order")
    target_model = models.CharField(max_length=100, help_text="e.g., 'Product' or 'Order'")
    
    class Meta:
        db_table = 'azt_workflow_states'
        # Ensures you don't accidentally create two "Pending" states for "Product"
        unique_together = ('name', 'target_model')
        
    def __str__(self):
        return f"{self.target_model}: {self.name}"

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