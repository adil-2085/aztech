from functools import wraps
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied


def inventory_manager_required(view_func):
    """
    Page-level equivalent of dashboard.permissions.IsInventoryManager, for
    plain Django (non-DRF) views. Without this, the HTML shell for the
    product management pages would be visible to anyone — the DRF API
    underneath is protected, but the page itself wasn't.
    """
    @wraps(view_func)
    @login_required(login_url='/admin/login/')
    def wrapper(request, *args, **kwargs):
        user = request.user
        if user.is_superuser or (user.role_id and user.role.can_manage_inventory):
            return view_func(request, *args, **kwargs)
        raise PermissionDenied("You don't have permission to manage inventory.")
    return wrapper