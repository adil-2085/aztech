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
    
    # NEW: Dynamic Brand Colors
    primary_color = models.CharField(max_length=7, default="#d01345", help_text="Main action color (Hex)")
    secondary_color = models.CharField(max_length=7, default="#2d2d2d", help_text="Main text/dark color (Hex)")
    
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


# ==========================================
# CATALOG STRUCTURE
# ==========================================

class Category(BaseModel):
    name = models.CharField(max_length=100)
    # A slug is a URL-friendly version of the name (e.g., "Mens Shoes" -> "mens-shoes")
    slug = models.SlugField(max_length=100, unique=True)
    description = models.TextField(blank=True, null=True)

    class Meta:
        db_table = 'azt_categories'
        verbose_name_plural = 'Categories'

    def __str__(self):
        return self.name


class Brand(BaseModel):
    name = models.CharField(max_length=100)
    slug = models.SlugField(max_length=100, unique=True)

    class Meta:
        db_table = 'azt_brands'

    def __str__(self):
        return self.name


# ==========================================
# PRODUCT
# ==========================================

class Product(BaseModel):
    # Relationships
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='products')
    brand = models.ForeignKey(Brand, on_delete=models.SET_NULL, null=True, blank=True, related_name='products')

    # Details
    title = models.CharField(max_length=255)
    slug = models.SlugField(max_length=255, unique=True)
    description = models.TextField()

    # Pricing & Inventory (For the ERP)
    # max_digits=10 means up to 99,999,999.99
    price = models.DecimalField(max_digits=10, decimal_places=2)
    compare_at_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, help_text="For showing 'Sale' discounts")
    cost_per_item = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, help_text="Internal cost for ERP profit calculations — never expose this in a public-facing serializer")

    # NOTE: stock_quantity here is the base/fallback stock level for products
    # that have no variants. Once a product has ProductVariant rows, the
    # variants' own stock_quantity is what actually gets sold against.
    stock_quantity = models.IntegerField(default=0)
    sku = models.CharField(max_length=100, unique=True, help_text="Stock Keeping Unit")

    class Meta:
        db_table = 'azt_products'
        ordering = ['-created_at']  # Show newest products first

    def __str__(self):
        return self.title

    @property
    def primary_image(self):
        """Convenience accessor for templates/serializers — falls back to the first image."""
        return self.images.filter(is_primary=True).first() or self.images.first()

    @property
    def has_variants(self):
        return self.variants.exists()


# ==========================================
# PRODUCT GALLERY
# ==========================================

class ProductImage(BaseModel):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='images')
    image = models.ImageField(upload_to='products/gallery/')
    alt_text = models.CharField(max_length=255, blank=True)

    # This is a display flag, not a lifecycle/workflow flag, so it's fine
    # alongside BaseModel's status field rather than replacing it.
    is_primary = models.BooleanField(default=False, help_text="Cover image shown on listing cards")
    display_order = models.PositiveIntegerField(default=0)

    class Meta:
        db_table = 'azt_product_images'
        ordering = ['display_order', 'created_at']

    def __str__(self):
        return f"{self.product.title} — image #{self.display_order}"


# ==========================================
# PRODUCT VARIANTS
# ==========================================

class ProductVariant(BaseModel):
    """
    A purchasable variation of a Product (e.g. Size: M, Color: Red).

    Deliberately generic (attribute_name/attribute_value) rather than
    hardcoded size/color columns, so a new variant axis (e.g. "Material")
    doesn't need a schema change later.
    """
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='variants')

    attribute_name = models.CharField(max_length=50, help_text="e.g. 'Size', 'Color'")
    attribute_value = models.CharField(max_length=50, help_text="e.g. 'M', 'Red'")

    sku = models.CharField(max_length=100, unique=True)
    stock_quantity = models.IntegerField(default=0)

    # Blank = falls back to the parent Product's price (see `price` property below).
    price_override = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)

    class Meta:
        db_table = 'azt_product_variants'
        unique_together = ('product', 'attribute_name', 'attribute_value')
        ordering = ['attribute_name', 'attribute_value']

    def __str__(self):
        return f"{self.product.title} — {self.attribute_name}: {self.attribute_value}"

    @property
    def price(self):
        return self.price_override if self.price_override is not None else self.product.price