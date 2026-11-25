
from django.urls import path

from .views import (
    PlacementDriveListCreateView,
    PlacementDriveDetailView,
    DriveEligibilityCreateView,
    DriveEligibilityDetailView,
    DriveRegistrationListCreateView,
    DriveRegistrationDetailView,
)


urlpatterns = [

    # Placement Drives

    path(
        '',
        PlacementDriveListCreateView.as_view(),
        name='drive-list-create'
    ),

    path(
        '<int:pk>/',
        PlacementDriveDetailView.as_view(),
        name='drive-detail'
    ),

    # Drive Eligibility

    path(
        '<int:drive_pk>/eligibility/',
        DriveEligibilityCreateView.as_view(),
        name='drive-eligibility-create'
    ),

    path(
        '<int:drive_pk>/eligibility/detail/',
        DriveEligibilityDetailView.as_view(),
        name='drive-eligibility-detail'
    ),

    # Drive Registration

    path(
        'registrations/',
        DriveRegistrationListCreateView.as_view(),
        name='drive-registration-list-create'
    ),

    path(
        'registrations/<int:pk>/',
        DriveRegistrationDetailView.as_view(),
        name='drive-registration-detail'
    ),

]
