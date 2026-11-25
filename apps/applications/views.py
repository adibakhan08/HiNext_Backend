
from django.utils import timezone
from django.shortcuts import get_object_or_404
from django.db import transaction, IntegrityError

from rest_framework import generics, status
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.exceptions import (
    PermissionDenied,
    ValidationError
)

from .models import (
    Application,
    ApplicationStatusHistory
)

from .serializers import (
    ApplicationSerializer,
    ApplicationStatusSerializer,
    ApplicationStatusHistorySerializer,
    ApplicationTrackingSerializer
)

from .permissions import IsNexHireAdmin

from apps.candidates.models import CandidateProfile
from apps.drives.models import DriveRegistration



# ==========================================
# HELPER FUNCTIONS
# ==========================================

def is_admin(user):

    return (
        user.is_authenticated
        and user.role == 'ADMIN'
        and user.is_staff
    )


def get_candidate(user):

    try:
        return CandidateProfile.objects.get(user=user)

    except CandidateProfile.DoesNotExist:

        raise ValidationError(
            'Candidate profile does not exist. Please complete your profile.'
        )


# ==========================================
# 1. APPLICATION LIST AND CREATE
# ==========================================

class ApplicationListCreateView(generics.ListCreateAPIView):

    serializer_class = ApplicationSerializer

    permission_classes = [IsAuthenticated]

    def get_queryset(self):

        queryset = Application.objects.select_related(
            'candidate',
            'candidate__user',
            'drive',
            'drive__company',
            'resume'
        ).prefetch_related(
            'status_history'
        )

        user = self.request.user

        # Admin can view all applications
        if is_admin(user):

            drive_id = self.request.query_params.get('drive')

            if drive_id:
                queryset = queryset.filter(
                    drive_id=drive_id
                )

            candidate_id = self.request.query_params.get('candidate')

            if candidate_id:
                queryset = queryset.filter(
                    candidate_id=candidate_id
                )

            application_status = self.request.query_params.get('status')

            if application_status:
                queryset = queryset.filter(
                    status=application_status
                )

            return queryset

        # Students can view only their own applications
        if user.role == 'STUDENT':

            return queryset.filter(
                candidate__user=user
            )

        return Application.objects.none()

    def create(self, request, *args, **kwargs):

        if request.user.role != 'STUDENT':

            raise PermissionDenied(
                'Only students can submit applications.'
            )

        candidate = get_candidate(request.user)

        serializer = self.get_serializer(
            data=request.data
        )

        serializer.is_valid(raise_exception=True)

        try:

            with transaction.atomic():

                application = serializer.save(
                    candidate=candidate
                )

                # Create initial application history
                ApplicationStatusHistory.objects.create(
                    application=application,
                    previous_status='',
                    new_status='APPLIED',
                    changed_by=request.user,
                    remarks='Application submitted.'
                )

        except IntegrityError:

            raise ValidationError(
                'You have already applied for this drive.'
            )

        response_serializer = self.get_serializer(
            application
        )

        return Response(
            response_serializer.data,
            status=status.HTTP_201_CREATED
        )


# ==========================================
# 2. APPLICATION DETAIL
# ==========================================

class ApplicationDetailView(generics.RetrieveAPIView):

    serializer_class = ApplicationSerializer

    permission_classes = [IsAuthenticated]

    def get_queryset(self):

        queryset = Application.objects.select_related(
            'candidate',
            'candidate__user',
            'drive',
            'drive__company',
            'resume'
        )

        user = self.request.user

        if is_admin(user):
            return queryset

        if user.role == 'STUDENT':

            return queryset.filter(
                candidate__user=user
            )

        return Application.objects.none()


# ==========================================
# 3. ADMIN UPDATE APPLICATION STATUS
# ==========================================

class ApplicationStatusUpdateView(generics.UpdateAPIView):

    serializer_class = ApplicationStatusSerializer

    permission_classes = [
        IsAuthenticated,
        IsNexHireAdmin
    ]

    queryset = Application.objects.select_related(
        'candidate',
        'drive'
    )

    def update(self, request, *args, **kwargs):

        partial = kwargs.pop('partial', False)

        with transaction.atomic():

            instance = self.get_object()

            previous_status = instance.status

            serializer = self.get_serializer(
                instance,
                data=request.data,
                partial=partial
            )

            serializer.is_valid(
                raise_exception=True
            )

            application = serializer.save()

            # Record history only when status changes
            if previous_status != application.status:

                ApplicationStatusHistory.objects.create(
                    application=application,
                    previous_status=previous_status,
                    new_status=application.status,
                    changed_by=request.user,
                    remarks=application.remarks
                )

        return Response(
            serializer.data,
            status=status.HTTP_200_OK
        )


# ==========================================
# 4. STUDENT WITHDRAW APPLICATION
# ==========================================


class ApplicationWithdrawView(APIView):

    permission_classes = [IsAuthenticated]

    def post(self, request, pk):

        if request.user.role != 'STUDENT':

            raise PermissionDenied(
                'Only students can withdraw applications.'
            )

        with transaction.atomic():

            application = get_object_or_404(
                Application.objects.select_for_update(),
                pk=pk,
                candidate__user=request.user
            )

            if application.status in [
                'REJECTED',
                'ACCEPTED',
                'DECLINED',
                'WITHDRAWN',
                'OFFERED',
                'SELECTED'
            ]:

                raise ValidationError(
                    'This application cannot be withdrawn at its current stage.'
                )

            previous_status = application.status

            application.status = 'WITHDRAWN'

            application.remarks = (
                'Application withdrawn by candidate.'
            )

            application.save(
                update_fields=[
                    'status',
                    'remarks',
                    'updated_at'
                ]
            )

            ApplicationStatusHistory.objects.create(
                application=application,
                previous_status=previous_status,
                new_status='WITHDRAWN',
                changed_by=request.user,
                remarks=application.remarks
            )

        return Response(
            {
                'message': 'Application withdrawn successfully.',
                'application_id': application.id,
                'status': application.status
            },
            status=status.HTTP_200_OK
        )


# ==========================================
# 5. APPLICATION STATUS HISTORY
# ==========================================

class ApplicationHistoryView(generics.ListAPIView):

    serializer_class = ApplicationStatusHistorySerializer

    permission_classes = [IsAuthenticated]

    def get_queryset(self):

        application_id = self.kwargs['pk']

        queryset = ApplicationStatusHistory.objects.filter(
            application_id=application_id
        ).select_related(
            'application',
            'changed_by'
        )

        user = self.request.user

        if is_admin(user):
            return queryset

        if user.role == 'STUDENT':

            return queryset.filter(
                application__candidate__user=user
            )

        return ApplicationStatusHistory.objects.none()


# ==========================================
# 6. LIST OF REG DRIVE
# ==========================================

class AvailableDrivesView(generics.ListAPIView):

    permission_classes = [IsAuthenticated]

    def get_queryset(self):

        user = self.request.user

        if user.role != 'STUDENT':
            raise PermissionDenied(
                'Only students can access registered drives.'
            )

        try:
            candidate = CandidateProfile.objects.get(user=user)
        except CandidateProfile.DoesNotExist:
            return DriveRegistration.objects.none()

        return DriveRegistration.objects.filter(
            candidate=candidate,
            eligibility_status='ELIGIBLE',
            registration_status='REGISTERED',
            drive__status='OPEN',
            drive__application_start_date__lte=timezone.now(),
            drive__application_deadline__gte=timezone.now()
        ).select_related(
            'drive',
            'drive__company'
        ).prefetch_related(
            'drive__applications'
        ).order_by('-registered_at')

    def list(self, request, *args, **kwargs):

        registrations = self.get_queryset()

        results = []

        for registration in registrations:

            drive = registration.drive

            application = drive.applications.filter(
                candidate=registration.candidate
            ).first()

            results.append({
                'registration_id': registration.id,
                'drive_id': drive.id,
                'drive_title': drive.title,
                'company_name': drive.company.name,
                'job_role': drive.job_role,
                'job_type': drive.job_type,
                'package_min': drive.package_min,
                'package_max': drive.package_max,
                'location': drive.location,
                'application_deadline': drive.application_deadline,
                'eligibility_status': registration.eligibility_status,
                'registration_status': registration.registration_status,
                'is_applied': application is not None,
                'application_id': application.id if application else None,
                'application_status': application.status if application else None
            })

        return Response({
            'count': len(results),
            'results': results
        })



class StudentApplicationTrackingView(generics.ListAPIView):

    serializer_class = ApplicationTrackingSerializer

    permission_classes = [
        IsAuthenticated
    ]

    def get_queryset(self):

        user = self.request.user

        # Only students can access this API
        if user.role != "STUDENT":

            raise PermissionDenied(
                "Only students can track their applications."
            )

        return (
            Application.objects

            .filter(
                candidate__user=user
            )

            .select_related(
                "candidate",
                "drive",
                "drive__company",
            )

            .prefetch_related(
                "status_history",
                "interviews",
                "interviews__interview_round",
            )

            .order_by("-applied_at")
        )