
from rest_framework.permissions import BasePermission


class IsNexHireAdmin(BasePermission):

    def has_permission(self, request, view):

        return (
            request.user.is_authenticated
            and request.user.role == 'ADMIN'
            and request.user.is_staff
        )


class IsStudent(BasePermission):

    def has_permission(self, request, view):

        return (
            request.user.is_authenticated
            and request.user.role == 'STUDENT'
        )
