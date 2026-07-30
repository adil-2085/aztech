from django.shortcuts import render
from rest_framework import generics
from .models import Product
from .serializers import ProductSerializer

# This endpoint will return JSON data for your product list
class ProductListAPIView(generics.ListAPIView):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer