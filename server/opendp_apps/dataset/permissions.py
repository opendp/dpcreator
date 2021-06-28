from rest_framework import permissions


class IsOwnerOrBlocked(permissions.BasePermission):
    """
    Only allow if user is creator
    """

    def has_object_permission(self, request, view, obj):
        return obj.creator == request.user
