from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    
    # Points the root URL (e.g., localhost:8000/) to the store app's urls.py
    path('', include('store.urls')),
    
    # Add other modular URLs here as you build them
    # path('dashboard/', include('dashboard.urls')),
]

# This allows Django to serve uploaded images (like product photos) locally
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)