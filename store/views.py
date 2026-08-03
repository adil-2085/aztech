from django.shortcuts import render, get_object_or_404
from rest_framework import generics
from utils.models import Product
from .serializers import ProductListSerializer, ProductDetailSerializer


# ==========================================
# DRF API — consumed by static/js/main.js
# ==========================================

class ProductListAPIView(generics.ListAPIView):
    """
    GET /api/products/
    Optional query params: ?category=<slug>&brand=<slug>
    """
    serializer_class = ProductListSerializer

    def get_queryset(self):
        queryset = (
            Product.objects.select_related('category', 'brand')
            .prefetch_related('images', 'variants')
            .filter(status__label='Published')
        )
        category_slug = self.request.query_params.get('category')
        brand_slug = self.request.query_params.get('brand')
        if category_slug:
            queryset = queryset.filter(category__slug=category_slug)
        if brand_slug:
            queryset = queryset.filter(brand__slug=brand_slug)
        return queryset


class ProductDetailAPIView(generics.RetrieveAPIView):
    """GET /api/products/<slug>/detail/"""
    queryset = (
        Product.objects.select_related('category', 'brand')
        .prefetch_related('images', 'variants')
        .filter(status__label='Published')
    )
    serializer_class = ProductDetailSerializer
    lookup_field = 'slug'


# ==========================================
# MVT PAGES — render the shell, JS fetches the data
# ==========================================

def storefront_home(request):
    """Product grid landing page (store/index.html)."""
    return render(request, 'store/index.html')


def product_detail(request, slug):
    """Single product page — confirms the product exists and is published,
    then lets main.js fetch the full detail payload from the API above."""
    product = get_object_or_404(Product, slug=slug, status__label='Published')
    return render(request, 'store/product_detail.html', {'product': product})