
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from apps.interviews.models import InterviewRound, Interview
from apps.interviews.serializers import (
    InterviewRoundSerializer,
    InterviewSerializer,
    InterviewResultSerializer,
)
from apps.interviews.permissions import (
    InterviewPermission,
    is_admin,
)


class InterviewRoundViewSet(viewsets.ModelViewSet):

    serializer_class = InterviewRoundSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        queryset = InterviewRound.objects.select_related(
            "drive"
        ).all()

        drive_id = self.request.query_params.get("drive")

        if drive_id:
            queryset = queryset.filter(drive_id=drive_id)

        return queryset

    def perform_create(self, serializer):
        if not is_admin(self.request.user):
            from rest_framework.exceptions import PermissionDenied
            raise PermissionDenied(
                "Only admins can create interview rounds."
            )

        serializer.save()

    def perform_update(self, serializer):
        if not is_admin(self.request.user):
            from rest_framework.exceptions import PermissionDenied
            raise PermissionDenied(
                "Only admins can update interview rounds."
            )

        serializer.save()

    def destroy(self, request, *args, **kwargs):
        if not is_admin(request.user):
            from rest_framework.exceptions import PermissionDenied
            raise PermissionDenied(
                "Only admins can delete interview rounds."
            )

        return super().destroy(request, *args, **kwargs)

    def create(self, request, *args, **kwargs):
        if not is_admin(request.user):
            from rest_framework.exceptions import PermissionDenied
            raise PermissionDenied(
                "Only admins can create interview rounds."
            )

        return super().create(request, *args, **kwargs)


class InterviewViewSet(viewsets.ModelViewSet):

    serializer_class = InterviewSerializer
    permission_classes = [InterviewPermission]

    def get_queryset(self):

        user = self.request.user

        queryset = Interview.objects.select_related(
            "application",
            "application__candidate",
            "application__candidate__user",
            "application__drive",
            "interview_round",
            "interviewer",
        )

        if is_admin(user):
            pass

        elif user.role == "STUDENT":
            queryset = queryset.filter(
                application__candidate__user=user
            )

        else:
            queryset = queryset.filter(
                interviewer=user
            )

        # Filters
        drive = self.request.query_params.get("drive")
        round_id = self.request.query_params.get("round")
        candidate = self.request.query_params.get("candidate")
        interview_status = self.request.query_params.get("status")
        result = self.request.query_params.get("result")

        if drive:
            queryset = queryset.filter(
                application__drive_id=drive
            )

        if round_id:
            queryset = queryset.filter(
                interview_round_id=round_id
            )

        if candidate:
            queryset = queryset.filter(
                application__candidate_id=candidate
            )

        if interview_status:
            queryset = queryset.filter(
                status=interview_status
            )

        if result:
            queryset = queryset.filter(
                result=result
            )

        return queryset.order_by("scheduled_at")

    def create(self, request, *args, **kwargs):

        if not is_admin(request.user):
            from rest_framework.exceptions import PermissionDenied
            raise PermissionDenied(
                "Only admins can schedule interviews."
            )

        return super().create(request, *args, **kwargs)

    def update(self, request, *args, **kwargs):

        if not is_admin(request.user):
            from rest_framework.exceptions import PermissionDenied
            raise PermissionDenied(
                "Only admins can update interview schedules."
            )

        return super().update(request, *args, **kwargs)

    def partial_update(self, request, *args, **kwargs):

        if not is_admin(request.user):
            from rest_framework.exceptions import PermissionDenied
            raise PermissionDenied(
                "Only admins can update interview schedules."
            )

        return super().partial_update(request, *args, **kwargs)

    def destroy(self, request, *args, **kwargs):

        if not is_admin(request.user):
            from rest_framework.exceptions import PermissionDenied
            raise PermissionDenied(
                "Only admins can delete interviews."
            )

        return super().destroy(request, *args, **kwargs)

    @action(
        detail=True,
        methods=["post"],
        url_path="result"
    )
    def result(self, request, pk=None):

        interview = self.get_object()

        # Only admins and the assigned interviewer
        # can submit evaluation results.
        if (
            not is_admin(request.user)
            and interview.interviewer_id != request.user.id
        ):
            from rest_framework.exceptions import PermissionDenied
            raise PermissionDenied(
                "You are not authorized to evaluate this interview."
            )

        serializer = InterviewResultSerializer(
            interview,
            data=request.data,
            partial=True
        )

        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(
            {
                "message": "Interview evaluation updated successfully.",
                "interview": InterviewSerializer(
                    interview,
                    context={"request": request}
                ).data
            },
            status=status.HTTP_200_OK
        )
