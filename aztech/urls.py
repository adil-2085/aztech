from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    # ... your existing paths ...
    path('', include('store.urls')),
]

# This allows Django to serve uploaded MEDIA files locally during development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    # You can also add static files here if needed, but Django handles them automatically in DEBUG mode
    # urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
# This allows Django to serve uploaded images (like product photos) locally
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)