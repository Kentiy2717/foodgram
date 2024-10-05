from rest_framework import permissions


class IsAuthenticatedOwnerOrReadOnly(permissions.IsAuthenticated):

    methods = (request.method in permissions.SAFE_METHODS)
    
    def has_permission(self, request, view):
        return bool(
            self.methods
            or request.user and request.user.is_authenticated
        )

    def has_object_permission(self, request, view, obj):
        return bool(
            self.methods
            or obj.author == request.user
        )
