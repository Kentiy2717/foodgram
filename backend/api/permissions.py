from rest_framework import permissions

methods = (request.method in permissions.SAFE_METHODS)


class IsAuthenticatedOwnerOrReadOnly(permissions.IsAuthenticated):
    def has_permission(self, request, view):
        return bool(
            methods
            or request.user and request.user.is_authenticated
        )

    def has_object_permission(self, request, view, obj):
        return bool(
            methods
            or obj.author == request.user
        )
