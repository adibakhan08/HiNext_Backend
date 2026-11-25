
from rest_framework.permissions import BasePermission


def is_admin(user):
    return (
        user.is_authenticated
        and user.role == "ADMIN"
        and user.is_staff
    )


class InterviewPermission(BasePermission):

    def has_permission(self, request, view):

        if not request.user.is_authenticated:
            return False

        if is_admin(request.user):
            return True

        # Students can only use read-only methods.
        if request.user.role == "STUDENT":
            return request.method in ["GET", "HEAD", "OPTIONS"]

        # Assigned interviewers can read interviews.
        if request.method in ["GET", "HEAD", "OPTIONS"]:
            return True

        return False

    def has_object_permission(self, request, view, obj):

        user = request.user

        if is_admin(user):
            return True

        # Student can access only their own interview.
        candidate = obj.application.candidate

        if (
            user.role == "STUDENT"
            and candidate.user_id == user.id
        ):
            return request.method in ["GET", "HEAD", "OPTIONS"]

        # Assigned interviewer can access their interviews.
        if obj.interviewer_id == user.id:
            return True

        return False
