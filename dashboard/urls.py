from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

app_name = 'dashboard'

router = DefaultRouter()
router.register('api/products', views.ProductAdminViewSet, basename='admin-product')
router.register('api/product-images', views.ProductImageAdminViewSet, basename='admin-product-image')
router.register('api/product-variants', views.ProductVariantAdminViewSet, basename='admin-product-variant')

urlpatterns = [
    # Pages
    path('products/', views.product_list_page, name='product-list'),
    path('products/new/', views.product_form_page, name='product-create'),
    path('products/<uuid:product_id>/edit/', views.product_form_page, name='product-edit'),

    # Read-only dropdown data
    path('api/categories/', views.CategoryOptionListAPIView.as_view(), name='category-options'),
    path('api/brands/', views.BrandOptionListAPIView.as_view(), name='brand-options'),
    path('api/workflow-states/', views.WorkflowStateOptionListAPIView.as_view(), name='workflow-state-options'),

    # Product/image/variant CRUD
    path('', include(router.urls)),
]