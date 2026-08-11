from rest_framework import permissions


class IsAdmin(permissions.BasePermission):
    """
    Предназначен для управления пользователями.
    Доступ только администратору или суперюзеру Django.
    """

    def has_permission(self, request, view):
        return (
            request.user.is_authenticated
            and request.user.is_admin
        )


class IsAdminOrReadOnly(permissions.BasePermission):
    """
    Предназначен для ограничения создания новых объектов проекта.
    Чтение всем, изменение только админам.
    """
    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True
        return (
            request.user.is_authenticated
            and request.user.is_admin
        )


class IsAuthorOrReadOnly(permissions.BasePermission):
    """
    Предназначен для управления объектами проекта,
    при условии, что автором объекта является текущий пользователь.
    """
    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        return obj.author == request.user


class IsAuthorModeratorAdminOrReadOnly(permissions.BasePermission):
    """
    Предназначен для ....:
    Чтение всем, писать комменты/отзывы может только авторизованный,
    Удалять и редактировать могут только автор, модераторы и админы.
    """
    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True
        return request.user.is_authenticated

    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True

        return (
            request.user.is_authenticated and (
                obj.author == request.user
                or request.user.is_moderator
                or request.user.is_admin
            )
        )
