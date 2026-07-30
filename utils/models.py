from django.db import models
from django.contrib.auth.models import AbstractUser
from base_utils.models import BaseModel
import uuid

# ==========================================
# ROLE MODEL (Dynamic Roles)
# ==========================================

class Role(BaseModel):
    name = models.CharField(max_length=50, unique=True) # e.g., "Accountant", "Manager"
    description = models.TextField(blank=True, null=True)
    
    # PRO TIP: Since roles are dynamic, you need a way to tell the system what 
    # this specific role is allowed to do. You can use boolean flags like these:
    can_view_financials = models.BooleanField(default=False)
    can_manage_inventory = models.BooleanField(default=False)
    can_manage_employees = models.BooleanField(default=False)

    class Meta:
        db_table = 'azt_roles'

    def __str__(self):
        return self.name

# ==========================================
# USER MODELS
# ==========================================

class CustomUser(AbstractUser):
    # Optional: use UUID for users too, for better security
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    # We replace the hardcoded choices with a relationship to the Role table.
    # on_delete=models.SET_NULL means if a role is deleted, the user isn't deleted, 
    # they just lose that role (it becomes empty).
    role = models.ForeignKey(Role, on_delete=models.SET_NULL, null=True, blank=True, related_name='users')
    
    # Optional: Fields specific to employees
    employee_id = models.CharField(max_length=50, blank=True, null=True)

    class Meta:
        # Explicitly define the database table name
        db_table = 'azt_users'

    def __str__(self):
        role_name = self.role.name if self.role else "No Role"
        return f"{self.username} ({role_name})"

# ==========================================
# STORE SETTINGS MODELS
# ==========================================

class StoreSettings(models.Model):
    brand_name = models.CharField(max_length=100, default="Loom")
    contact_email = models.EmailField(default="contact@loom.com")
    
    # Standard timestamps (we don't inherit BaseModel here to keep the ID simple)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name_plural = 'Store Settings'
        # Explicitly define the database table name
        db_table = 'azt_store_settings'

    def save(self, *args, **kwargs):
        # Overrides the save method to ensure only ONE row ever exists (Singleton pattern)
        self.pk = 1 
        super(StoreSettings, self).save(*args, **kwargs)

    def __str__(self):
        return f"Settings for: {self.brand_name}"