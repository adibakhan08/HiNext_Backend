
from django.urls import path

from apps.analytics.views import (
    AnalyticsOverviewView,
    PlacementTrendsView,
    ApplicationTrendsView,
    ApplicationStatusView,
    DepartmentWiseAnalyticsView,
    CompanyWiseAnalyticsView,
    PackageAnalysisView,
    DrivePerformanceView,
    InterviewAnalysisView,
    UnplacedStudentsView,
)

urlpatterns = [

    path(
        "overview/",
        AnalyticsOverviewView.as_view(),
        name="analytics-overview"
    ),

    path(
        "placement-trends/",
        PlacementTrendsView.as_view(),
        name="placement-trends"
    ),

    path(
        "application-trends/",
        ApplicationTrendsView.as_view(),
        name="application-trends"
    ),

    path(
        "application-status/",
        ApplicationStatusView.as_view(),
        name="application-status"
    ),

    path(
        "department-wise/",
        DepartmentWiseAnalyticsView.as_view(),
        name="department-wise"
    ),

    path(
        "company-wise/",
        CompanyWiseAnalyticsView.as_view(),
        name="company-wise"
    ),

    path(
        "package-analysis/",
        PackageAnalysisView.as_view(),
        name="package-analysis"
    ),

    path(
        "drive-performance/",
        DrivePerformanceView.as_view(),
        name="drive-performance"
    ),

    path(
        "interview-analysis/",
        InterviewAnalysisView.as_view(),
        name="interview-analysis"
    ),

    path(
        "unplaced-students/",
        UnplacedStudentsView.as_view(),
        name="unplaced-students"
    ),
]
