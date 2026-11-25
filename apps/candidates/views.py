
from django.shortcuts import get_object_or_404

from rest_framework import generics, filters
from rest_framework.permissions import IsAuthenticated
from rest_framework.exceptions import PermissionDenied

from .models import (
    CandidateProfile,
    Education,
    CandidateSkill,
    Resume
)

from .serializers import (
    CandidateProfileSerializer,
    EducationSerializer,
    CandidateSkillSerializer,
    ResumeSerializer,
    AdminCandidateListSerializer,
    AdminCandidateDetailSerializer
)
from .permissions import IsAdminUserRole
from django_filters.rest_framework import DjangoFilterBackend



# Helper function

def get_candidate(user):

    if user.role != 'STUDENT':
        raise PermissionDenied(
            'Only students can access candidate profiles.'
        )

    return get_object_or_404(
        CandidateProfile,
        user=user
    )


# 1. Candidate Profile Creation

class CandidateProfileCreateView(generics.CreateAPIView):

    serializer_class = CandidateProfileSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):

        if self.request.user.role != 'STUDENT':
            raise PermissionDenied(
                'Only students can create candidate profiles.'
            )

        if CandidateProfile.objects.filter(
            user=self.request.user
        ).exists():
            raise PermissionDenied(
                'Candidate profile already exists.'
            )

        serializer.save(user=self.request.user)


# 2. Candidate Profile Retrieve / Update

class CandidateProfileView(generics.RetrieveUpdateAPIView):

    serializer_class = CandidateProfileSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):

        return get_candidate(self.request.user)


# 3. Education List / Create

class EducationListCreateView(generics.ListCreateAPIView):

    serializer_class = EducationSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):

        candidate = get_candidate(self.request.user)

        return Education.objects.filter(
            candidate=candidate
        )

    def perform_create(self, serializer):

        candidate = get_candidate(self.request.user)

        serializer.save(candidate=candidate)


# 4. Education Retrieve / Update / Delete

class EducationDetailView(generics.RetrieveUpdateDestroyAPIView):

    serializer_class = EducationSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):

        candidate = get_candidate(self.request.user)

        return Education.objects.filter(
            candidate=candidate
        )


# 5. Candidate Skills List / Create

class CandidateSkillListCreateView(generics.ListCreateAPIView):

    serializer_class = CandidateSkillSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):

        candidate = get_candidate(self.request.user)

        return CandidateSkill.objects.filter(
            candidate=candidate
        ).select_related('skill')

    def perform_create(self, serializer):

        candidate = get_candidate(self.request.user)

        serializer.save(candidate=candidate)


# 6. Candidate Skill Retrieve / Update / Delete

class CandidateSkillDetailView(generics.RetrieveUpdateDestroyAPIView):

    serializer_class = CandidateSkillSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):

        candidate = get_candidate(self.request.user)

        return CandidateSkill.objects.filter(
            candidate=candidate
        )


# 7. Resume List / Upload

class ResumeListCreateView(generics.ListCreateAPIView):

    serializer_class = ResumeSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):

        candidate = get_candidate(self.request.user)

        return Resume.objects.filter(
            candidate=candidate
        )

    def perform_create(self, serializer):

        candidate = get_candidate(self.request.user)

        serializer.save(candidate=candidate)


# 8. Resume Retrieve / Update / Delete

class ResumeDetailView(generics.RetrieveUpdateDestroyAPIView):

    serializer_class = ResumeSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):

        candidate = get_candidate(self.request.user)

        return Resume.objects.filter(
            candidate=candidate
        )

class AdminCandidateListView(generics.ListAPIView):

    serializer_class = AdminCandidateListSerializer

    permission_classes = [
        IsAdminUserRole
    ]

    queryset = CandidateProfile.objects.select_related(
        'user',
        'department',
        'course'
    ).all()

    filter_backends = [
        filters.SearchFilter,
        DjangoFilterBackend,
        filters.OrderingFilter
    ]

    search_fields = [
        'user__username',
        'user__first_name',
        'user__last_name',
        'user__email',
        'enrollment_number'
    ]

    filterset_fields = [
        'department',
        'course',
        'graduation_year'
    ]

    ordering_fields = [
        'created_at',
        'current_cgpa',
        'graduation_year',
        'enrollment_number'
    ]

    ordering = ['-created_at']


class AdminCandidateDetailView(generics.RetrieveAPIView):

    serializer_class = AdminCandidateDetailSerializer

    permission_classes = [
        IsAdminUserRole
    ]

    queryset = CandidateProfile.objects.select_related(
        'user',
        'department',
        'course'
    ).prefetch_related(
        'education',
        'candidate_skills__skill',
        'resumes'
    )

