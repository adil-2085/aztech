from django.urls import path
from . import views

app_name = 'store'

urlpatterns = [
    # Point the root URL of the store app to our new view
    path('', views.storefront_home, name='home'),
    path('api/products/', views.ProductListAPIView.as_view(), name='product-api'),
]