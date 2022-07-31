from rest_framework.permissions import SAFE_METHODS, BasePermission


class IsAuthorOrReadOnly(BasePermission):

    def has_object_permission(self, request, view, obj):
        return (
            request.method in SAFE_METHODS
            or request.method == 'POST' and request.user.is_autenticated
            or request.method in ['PUT', 'PATCH', 'DELETE']
            and (request.user == obj.author or request.user.is_superuser)
        )


class IsAdminOrReadOnly(BasePermission):

    def has_permission(self, request, view):
        return request.method in SAFE_METHODS or request.user.is_superuser
