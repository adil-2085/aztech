from rest_framework.permissions import BasePermission


class IsInventoryManager(BasePermission):
    """
    Grants access to logged-in users whose Role has can_manage_inventory=True.
    Superusers always pass, so a `createsuperuser` account is enough to test
    this window without needing a Role assigned first.
    """
    message = "You don't have permission to manage inventory."

    def has_permission(self, request, view):
        user = request.user
        if not user.is_authenticated:
            return False
        if user.is_superuser:
            return True
        return bool(user.role_id and user.role.can_manage_inventory)