from django.db import models
import uuid

class BaseModel(models.Model):
    # Using UUIDs instead of standard 1, 2, 3 IDs is much more secure for e-commerce
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    # These will automatically track when any object is created or modified
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        # This tells Django NOT to create a database table for this specific model.
        # Instead, other models will inherit these fields.
        abstract = True