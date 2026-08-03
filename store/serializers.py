from rest_framework import serializers
from utils.models import Product, ProductImage, ProductVariant, Category, Brand


class ProductImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductImage
        fields = ['id', 'image', 'alt_text', 'is_primary', 'display_order']


class ProductVariantSerializer(serializers.ModelSerializer):
    price = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)

    class Meta:
        model = ProductVariant
        fields = ['id', 'attribute_name', 'attribute_value', 'sku', 'stock_quantity', 'price']


class ProductListSerializer(serializers.ModelSerializer):
    """Lightweight serializer for the grid/listing view — one image, no variant detail."""
    primary_image = serializers.SerializerMethodField()
    category_name = serializers.CharField(source='category.name', read_only=True)
    category_slug = serializers.CharField(source='category.slug', read_only=True)
    brand_name = serializers.CharField(source='brand.name', read_only=True)
    has_variants = serializers.BooleanField(read_only=True)

    class Meta:
        model = Product
        fields = [
            'id', 'title', 'slug', 'price', 'compare_at_price',
            'category_name', 'category_slug', 'brand_name', 'primary_image', 'has_variants',
        ]
        # cost_per_item is intentionally excluded everywhere in this file —
        # it's an internal ERP field and must never reach the storefront API.

    def get_primary_image(self, obj):
        img = obj.primary_image
        if not img:
            return None
        request = self.context.get('request')
        url = img.image.url
        return request.build_absolute_uri(url) if request else url


class ProductDetailSerializer(serializers.ModelSerializer):
    """Full serializer for the single product page — all images + all variants."""
    images = ProductImageSerializer(many=True, read_only=True)
    variants = ProductVariantSerializer(many=True, read_only=True)
    category_name = serializers.CharField(source='category.name', read_only=True)
    brand_name = serializers.CharField(source='brand.name', read_only=True)

    class Meta:
        model = Product
        fields = [
            'id', 'title', 'slug', 'description',
            'price', 'compare_at_price', 'stock_quantity', 'sku',
            'category', 'category_name', 'brand', 'brand_name',
            'images', 'variants', 'created_at',
        ]