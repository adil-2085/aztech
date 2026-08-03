from django.shortcuts import render, get_object_or_404
from django.utils.text import slugify
from rest_framework import generics, viewsets
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser

from utils.models import Product, ProductImage, ProductVariant, Category, Brand
from base_utils.models import WorkflowState

from .permissions import IsInventoryManager
from .decorators import inventory_manager_required
from .serializers import (
    ProductAdminSerializer, ProductImageAdminSerializer, ProductVariantAdminSerializer,
    CategoryOptionSerializer, BrandOptionSerializer, WorkflowStateOptionSerializer,
)


# ==========================================
# PRODUCT CRUD (DRF) — consumed by static/js/dashboard.js
# ==========================================

class ProductAdminViewSet(viewsets.ModelViewSet):
    """Full CRUD for Product. Gated to IsInventoryManager."""
    permission_classes = [IsInventoryManager]
    serializer_class = ProductAdminSerializer
    queryset = Product.objects.select_related('category', 'brand', 'status').prefetch_related('images', 'variants')

    def perform_create(self, serializer):
        # Safety net: auto-slug from title if the form didn't send one.
        slug = serializer.validated_data.get('slug') or slugify(serializer.validated_data['title'])
        serializer.save(slug=slug)


class ProductImageAdminViewSet(viewsets.ModelViewSet):
    """CRUD for a single product's gallery images. Filter list by ?product=<id>."""
    permission_classes = [IsInventoryManager]
    serializer_class = ProductImageAdminSerializer
    parser_classes = [MultiPartParser, FormParser, JSONParser]

    def get_queryset(self):
        qs = ProductImage.objects.all()
        product_id = self.request.query_params.get('product')
        if product_id:
            qs = qs.filter(product_id=product_id)
        return qs


class ProductVariantAdminViewSet(viewsets.ModelViewSet):
    """CRUD for a single product's variants. Filter list by ?product=<id>."""
    permission_classes = [IsInventoryManager]
    serializer_class = ProductVariantAdminSerializer

    def get_queryset(self):
        qs = ProductVariant.objects.all()
        product_id = self.request.query_params.get('product')
        if product_id:
            qs = qs.filter(product_id=product_id)
        return qs


# ==========================================
# READ-ONLY OPTION LISTS — populate form dropdowns
# ==========================================

class CategoryOptionListAPIView(generics.ListAPIView):
    permission_classes = [IsInventoryManager]
    serializer_class = CategoryOptionSerializer
    queryset = Category.objects.all().order_by('name')


class BrandOptionListAPIView(generics.ListAPIView):
    permission_classes = [IsInventoryManager]
    serializer_class = BrandOptionSerializer
    queryset = Brand.objects.all().order_by('name')


class WorkflowStateOptionListAPIView(generics.ListAPIView):
    """GET /dashboard/api/workflow-states/ — states are a universal pool, not filtered per model."""
    permission_classes = [IsInventoryManager]
    serializer_class = WorkflowStateOptionSerializer
    queryset = WorkflowState.objects.all().order_by('label')


# ==========================================
# MVT PAGES
# ==========================================

@inventory_manager_required
def product_list_page(request):
    """The product management table (dashboard/product_list.html)."""
    return render(request, 'dashboard/product_list.html')


@inventory_manager_required
def product_form_page(request, product_id=None):
    """
    Add/edit form — same template for both. `product_id` is None when
    creating; dashboard.js reads data-product-id off the root element to
    decide whether to POST (create) or PATCH (edit).
    """
    product = None
    if product_id:
        product = get_object_or_404(Product, id=product_id)
    return render(request, 'dashboard/product_form.html', {'product': product})