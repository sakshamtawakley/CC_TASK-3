from rest_framework import permissions

class IsShopkeeper(permissions.BasePermission):
    """
    Custom permission to only allow shopkeepers to access certain views.
    """
    message = "Access denied. Shopkeeper privileges required."

    def has_permission(self, request, view):
        return (
            request.user and
            request.user.is_authenticated and
            request.user.role == 'shopkeeper'
        )

class IsUser(permissions.BasePermission):
    """
    Custom permission to only allow regular users to access certain views.
    """
    message = "Access denied. User privileges required."

    def has_permission(self, request, view):
        return (
            request.user and
            request.user.is_authenticated and
            request.user.role == 'user'
        )
