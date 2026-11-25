
from django.utils import timezone
from django.shortcuts import get_object_or_404
from django.db import IntegrityError, transaction
from django.db.models import Q

from rest_framework import generics, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.exceptions import (
    PermissionDenied,
    ValidationError
)

from .models import (
    PlacementDrive,
    DriveEligibility,
    DriveRegistration
)

from .serializers import (
    PlacementDriveSerializer,
    DriveEligibilitySerializer,
    DriveRegistrationSerializer,
    DriveRegistrationStatusSerializer
)

from .permissions import IsAdminOrReadOnly

from apps.candidates.models import CandidateProfile
from apps.calendar_app.services import sync_drive_calendar_events


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
            'Candidate profile does not exist. Please complete your profile first.'
        )


# ==========================================
# 1. PLACEMENT DRIVE LIST AND CREATE
# ==========================================

class PlacementDriveListCreateView(generics.ListCreateAPIView):

    serializer_class = PlacementDriveSerializer

    permission_classes = [
        IsAuthenticated,
        IsAdminOrReadOnly
    ]

    def get_queryset(self):
        
        queryset = PlacementDrive.objects.select_related(
            'company',
            'academic_session',
            'created_by'
        ).prefetch_related(
            'eligibility__eligible_departments',
            'eligibility__eligible_courses'
        )

        user = self.request.user

        # Students can see ALL drives
        # Admins can also see ALL drives

        # Filter by company
        company_id = self.request.query_params.get('company')

        if company_id:
            queryset = queryset.filter(
                company_id=company_id
            )

        # Filter by job type
        job_type = self.request.query_params.get('job_type')

        if job_type:
            queryset = queryset.filter(
                job_type=job_type
            )

        # Filter by status
        status_filter = self.request.query_params.get('status')

        if status_filter:
            queryset = queryset.filter(
                status=status_filter
            )

        # Search
        search = self.request.query_params.get('search')

        if search:
            queryset = queryset.filter(
                Q(title__icontains=search) |
                Q(job_role__icontains=search) |
                Q(company__name__icontains=search)
            )

        return queryset.order_by('-created_at')

    def perform_create(self, serializer):
        if not is_admin(self.request.user):
            raise PermissionDenied(
                'Only admins can create placement drives.'
            )

        with transaction.atomic():

            drive = serializer.save(
                created_by=self.request.user
            )

            sync_drive_calendar_events(
                drive,
                self.request.user
            )

    def perform_update(self, serializer):
        with transaction.atomic():

            drive = serializer.save()

            sync_drive_calendar_events(
                drive,
                self.request.user
            )

    def perform_destroy(self, instance):
        with transaction.atomic():

            instance.status = 'CANCELLED'
            instance.save(update_fields=['status'])

            sync_drive_calendar_events(
                instance,
                self.request.user
            )


# ==========================================
# 2. PLACEMENT DRIVE DETAIL
# ==========================================

class PlacementDriveDetailView(
    generics.RetrieveUpdateDestroyAPIView
):

    serializer_class = PlacementDriveSerializer

    permission_classes = [
        IsAuthenticated,
        IsAdminOrReadOnly
    ]

    def get_queryset(self):

        queryset = PlacementDrive.objects.select_related(
            'company',
            'academic_session',
            'created_by'
        ).prefetch_related(
            'eligibility__eligible_departments',
            'eligibility__eligible_courses'
        )

        user = self.request.user

        # Students can access only currently open drives
        # if not is_admin(user):

        #     now = timezone.now()

        #     queryset = queryset.filter(
        #         status='OPEN',
        #         application_start_date__lte=now,
        #         application_deadline__gte=now
        #     )

        return queryset


# ==========================================
# 3. CREATE DRIVE ELIGIBILITY
# ==========================================

class DriveEligibilityCreateView(generics.CreateAPIView):

    serializer_class = DriveEligibilitySerializer

    permission_classes = [
        IsAuthenticated
    ]

    def perform_create(self, serializer):

        if not is_admin(self.request.user):
            raise PermissionDenied(
                'Only admins can create eligibility criteria.'
            )

        drive = get_object_or_404(
            PlacementDrive,
            pk=self.kwargs['drive_pk']
        )

        if DriveEligibility.objects.filter(
            drive=drive
        ).exists():

            raise ValidationError(
                'Eligibility criteria already exist for this drive.'
            )

        serializer.save(
            drive=drive
        )


# ==========================================
# 4. DRIVE ELIGIBILITY DETAIL
# ==========================================

class DriveEligibilityDetailView(
    generics.RetrieveUpdateAPIView
):

    serializer_class = DriveEligibilitySerializer

    permission_classes = [
        IsAuthenticated
    ]

    def get_object(self):

        if not is_admin(self.request.user):
            raise PermissionDenied(
                'Only admins can manage eligibility criteria.'
            )

        return get_object_or_404(
            DriveEligibility,
            drive_id=self.kwargs['drive_pk']
        )


# ==========================================
# 5. CHECK CANDIDATE ELIGIBILITY
# ==========================================

def check_candidate_eligibility(candidate, drive):

    try:
        eligibility = drive.eligibility

    except DriveEligibility.DoesNotExist:

        return False, [
            'Eligibility criteria have not been configured.'
        ]

    reasons = []

    # CGPA check
    if candidate.current_cgpa is None:

        reasons.append(
            'Candidate CGPA is not available.'
        )

    elif candidate.current_cgpa < eligibility.minimum_cgpa:

        reasons.append(
            'Minimum CGPA requirement not met.'
        )

    # Backlog check
    if candidate.backlogs > eligibility.maximum_backlogs:

        reasons.append(
            'Maximum backlog requirement not met.'
        )

    # Graduation year check
    if candidate.graduation_year != eligibility.graduation_year:

        reasons.append(
            'Graduation year does not match.'
        )

    # Department check
    departments = eligibility.eligible_departments.all()

    if departments.exists():

        if not departments.filter(
            id=candidate.department_id
        ).exists():

            reasons.append(
                'Department is not eligible.'
            )

    # Course check
    courses = eligibility.eligible_courses.all()

    if courses.exists():

        if not courses.filter(
            id=candidate.course_id
        ).exists():

            reasons.append(
                'Course is not eligible.'
            )

    return len(reasons) == 0, reasons


# ==========================================
# 6. STUDENT DRIVE REGISTRATION
# ==========================================

class DriveRegistrationListCreateView(
    generics.ListCreateAPIView
):

    serializer_class = DriveRegistrationSerializer

    permission_classes = [
        IsAuthenticated
    ]

    def get_queryset(self):

        queryset = DriveRegistration.objects.select_related(
            'drive',
            'candidate',
            'candidate__user'
        )

        user = self.request.user

        # Admin can view all registrations
        if is_admin(user):

            drive_id = self.request.query_params.get('drive')

            if drive_id:
                queryset = queryset.filter(
                    drive_id=drive_id
                )

            return queryset

        # Students can view only their own registrations
        if user.role != 'STUDENT':
            return DriveRegistration.objects.none()

        return queryset.filter(
            candidate__user=user
        )

    def create(self, request, *args, **kwargs):

        user = request.user

        # Only students can register
        if user.role != 'STUDENT':
            raise PermissionDenied(
                'Only students can register for placement drives.'
            )

        # Get candidate profile
        candidate = get_candidate(user)

        drive_id = request.data.get('drive')

        if not drive_id:
            raise ValidationError({
                'drive': 'Drive ID is required.'
            })

        # Validate drive ID
        try:
            drive_id = int(drive_id)

            if drive_id <= 0:
                raise ValueError

        except (TypeError, ValueError):
            raise ValidationError({
                'drive': 'Please provide a valid drive ID.'
            })

        # Transaction ensures concurrent capacity checks
        try:

            with transaction.atomic():

                drive = get_object_or_404(
                    PlacementDrive.objects.select_for_update(),
                    pk=drive_id
                )

                now = timezone.now()

                # Drive status check
                if drive.status != 'OPEN':

                    raise ValidationError(
                        'This placement drive is not open.'
                    )

                # Application start check
                if now < drive.application_start_date:

                    raise ValidationError(
                        'Registration has not started yet.'
                    )

                # Application deadline check
                if now > drive.application_deadline:

                    raise ValidationError(
                        'Registration deadline has passed.'
                    )

                # Opening capacity check
                registered_count = DriveRegistration.objects.filter(
                    drive=drive,
                    registration_status='REGISTERED'
                ).count()

                if registered_count >= drive.openings:

                    raise ValidationError(
                        'All openings for this drive have been filled.'
                    )

                # Eligibility check
                eligible, reasons = check_candidate_eligibility(
                    candidate,
                    drive
                )

                if not eligible:

                    raise ValidationError({
                        'eligibility': reasons
                    })

                # Create registration
                registration = DriveRegistration.objects.create(
                    drive=drive,
                    candidate=candidate,
                    eligibility_status='ELIGIBLE',
                    registration_status='REGISTERED'
                )

        except IntegrityError:

            raise ValidationError(
                'You have already registered for this drive.'
            )

        serializer = self.get_serializer(registration)

        return Response(
            serializer.data,
            status=status.HTTP_201_CREATED
        )


# ==========================================
# 7. REGISTRATION DETAIL AND STATUS UPDATE
# ==========================================

class DriveRegistrationDetailView(
    generics.RetrieveUpdateAPIView
):

    serializer_class = DriveRegistrationSerializer

    permission_classes = [
        IsAuthenticated
    ]

    def get_serializer_class(self):

        if self.request.method in ['PUT', 'PATCH']:

            return DriveRegistrationStatusSerializer

        return DriveRegistrationSerializer

    def get_queryset(self):

        queryset = DriveRegistration.objects.select_related(
            'drive',
            'candidate',
            'candidate__user'
        )

        user = self.request.user

        # Admin can access all registrations
        if is_admin(user):
            return queryset

        # Students can access only their registrations
        if user.role == 'STUDENT':

            return queryset.filter(
                candidate__user=user
            )

        return DriveRegistration.objects.none()

    def update(self, request, *args, **kwargs):

        # Only admins can update registrations
        if not is_admin(request.user):

            raise PermissionDenied(
                'Only admins can update registration status.'
            )

        return super().update(
            request,
            *args,
            **kwargs
        )

