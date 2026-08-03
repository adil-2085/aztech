from rest_framework import serializers
from utils.models import Product, ProductImage, ProductVariant, Category, Brand
from base_utils.models import WorkflowState


class ProductImageAdminSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductImage
        fields = ['id', 'product', 'image', 'alt_text', 'is_primary', 'display_order']
        read_only_fields = ['id']


class ProductVariantAdminSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductVariant
        fields = ['id', 'product', 'attribute_name', 'attribute_value', 'sku', 'stock_quantity', 'price_override']
        read_only_fields = ['id']


class ProductAdminSerializer(serializers.ModelSerializer):
    """
    Full read/write serializer for internal product management.

    Unlike store.serializers (customer-facing, cost_per_item excluded by
    field list), this one is for employees and intentionally includes
    cost_per_item — access is controlled by dashboard.permissions
    .IsInventoryManager on the view, not by hiding the field here. Do not
    reuse this serializer anywhere the storefront/public API is served.
    """
    images = ProductImageAdminSerializer(many=True, read_only=True)
    variants = ProductVariantAdminSerializer(many=True, read_only=True)
    category_name = serializers.CharField(source='category.name', read_only=True)
    brand_name = serializers.CharField(source='brand.name', read_only=True)
    status_name = serializers.CharField(source='status.label', read_only=True)

    class Meta:
        model = Product
        fields = [
            'id', 'title', 'slug', 'description',
            'category', 'category_name', 'brand', 'brand_name',
            'price', 'compare_at_price', 'cost_per_item',
            'stock_quantity', 'sku',
            'status', 'status_name',
            'images', 'variants',
            'created_at', 'updated_at',
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class CategoryOptionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'name', 'slug']


class BrandOptionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Brand
        fields = ['id', 'name', 'slug']


class WorkflowStateOptionSerializer(serializers.ModelSerializer):
    class Meta:
        model = WorkflowState
        fields = ['id', 'label', 'slug', 'description']