
from django.urls import path

from .views import (
    ApplicationListCreateView,
    ApplicationDetailView,
    ApplicationStatusUpdateView,
    ApplicationWithdrawView,
    ApplicationHistoryView,
    AvailableDrivesView,
    StudentApplicationTrackingView
)


urlpatterns = [

    # Application List and Create

    path(
        '',
        ApplicationListCreateView.as_view(),
        name='application-list-create'
    ),

    # Application Details

    path(
        '<int:pk>/',
        ApplicationDetailView.as_view(),
        name='application-detail'
    ),

    # Update Application Status (Admin)

    path(
        '<int:pk>/status/',
        ApplicationStatusUpdateView.as_view(),
        name='application-status-update'
    ),

    # Withdraw Application (Student)

    path(
        '<int:pk>/withdraw/',
        ApplicationWithdrawView.as_view(),
        name='application-withdraw'
    ),

    # Application Status History

    path(
        '<int:pk>/history/',
        ApplicationHistoryView.as_view(),
        name='application-history'
    ),
    path(
        'available-drives/',
        AvailableDrivesView.as_view(),
        name='available-drives'
    ),
    path(
        "application-tracking/",
        StudentApplicationTrackingView.as_view(),
        name="student-application-tracking"
    ),

]
