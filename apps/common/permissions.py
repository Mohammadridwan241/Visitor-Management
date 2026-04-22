from rest_framework.permissions import BasePermission


class IsReceptionistOrAdmin(BasePermission):
    message = 'Receptionist or admin access is required.'

    def has_permission(self, request, view):
        user = request.user
        return bool(
            user
            and user.is_authenticated
            and (getattr(user, 'is_admin', False) or getattr(user, 'is_receptionist', False))
        )
