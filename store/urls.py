from django.urls import path
from . import views

app_name = 'store'

urlpatterns = [
    path('', views.storefront_home, name='home'),
    path('product/<slug:slug>/', views.product_detail, name='product-detail'),

    # DRF endpoints, consumed by static/js/main.js
    path('api/products/', views.ProductListAPIView.as_view(), name='product-api'),
    path('api/products/<slug:slug>/detail/', views.ProductDetailAPIView.as_view(), name='product-detail-api'),
]