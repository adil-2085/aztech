from .models import StoreSettings

def global_store_settings(request):
    # Fetch the single StoreSettings instance, or create it if it doesn't exist yet
    settings, created = StoreSettings.objects.get_or_create(pk=1)
    
    # Now, {{ store_settings }} is globally available in EVERY HTML file!
    return {'store_settings': settings}