
from django.urls import path

from .views import (
    CandidateProfileCreateView,
    CandidateProfileView,
    EducationListCreateView,
    EducationDetailView,
    CandidateSkillListCreateView,
    CandidateSkillDetailView,
    ResumeListCreateView,
    ResumeDetailView,
    AdminCandidateListView,
    AdminCandidateDetailView
)


urlpatterns = [

    # Candidate Profile
    path(
        'profile/create/',
        CandidateProfileCreateView.as_view(),
        name='candidate-profile-create'
    ),

    path(
        'profile/',
        CandidateProfileView.as_view(),
        name='candidate-profile'
    ),

    # Education
    path(
        'education/',
        EducationListCreateView.as_view(),
        name='education-list-create'
    ),

    path(
        'education/<int:pk>/',
        EducationDetailView.as_view(),
        name='education-detail'
    ),

    # Skills
    path(
        'skills/',
        CandidateSkillListCreateView.as_view(),
        name='candidate-skill-list-create'
    ),

    path(
        'skills/<int:pk>/',
        CandidateSkillDetailView.as_view(),
        name='candidate-skill-detail'
    ),

    # Resumes
    path(
        'resumes/',
        ResumeListCreateView.as_view(),
        name='resume-list-create'
    ),

    path(
        'resumes/<int:pk>/',
        ResumeDetailView.as_view(),
        name='resume-detail'
    ),
    path(
        'admin/candidates/',
        AdminCandidateListView.as_view(),
        name='admin-candidate-list'
    ),
    path(
        'admin/candidates/<int:pk>/',
        AdminCandidateDetailView.as_view(),
        name='admin-candidate-detail'
    ),
]
