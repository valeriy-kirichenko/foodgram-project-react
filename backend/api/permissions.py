from rest_framework.permissions import SAFE_METHODS, BasePermission


class IsAuthorOrReadOnly(BasePermission):
    """Разрешает доступ всем пользователям если метод запроса среди безопасных,
     либо для аутентифицированных пользователей при создании рецепта,
     либо если пользователь явлеяется автором рецепта при его изменении
     или удалении.
    """

    def has_object_permission(self, request, view, obj):
        return (
            request.method in SAFE_METHODS
            or request.method == 'POST' and request.user.is_autenticated
            or request.method in ['PUT', 'PATCH', 'DELETE']
            and (request.user == obj.author or request.user.is_superuser)
        )


class IsAdminOrReadOnly(BasePermission):
    """Разрешает доступ всем пользователям если метод запроса среди безопасных,
     либо если пользователь является администратором.
    """

    def has_permission(self, request, view):
        return request.method in SAFE_METHODS or request.user.is_superuser
