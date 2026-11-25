
from django.db.models import (
    Count,
    Avg,
    Max,
    Min,
    Q,
    F,
    Case,
    When,
    IntegerField,
    Value,
)
from django.db.models.functions import TruncMonth
from django.utils import timezone

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.exceptions import PermissionDenied
from rest_framework.pagination import PageNumberPagination

from apps.applications.models import (
    Application,
    ApplicationStatusHistory,
)
from apps.drives.models import PlacementDrive
from apps.candidates.models import CandidateProfile
from apps.interviews.models import Interview


# =====================================================
# COMMON ADMIN PERMISSION
# =====================================================

class AdminAnalyticsView(APIView):

    permission_classes = [IsAuthenticated]

    def check_permissions(self, request):
        super().check_permissions(request)

        if not (
            request.user.role == "ADMIN"
            and request.user.is_staff
        ):
            raise PermissionDenied(
                "Only admins can access analytics."
            )


# =====================================================
# 1. OVERVIEW ANALYTICS
# GET /api/analytics/overview/
# =====================================================

class AnalyticsOverviewView(AdminAnalyticsView):

    def get(self, request):

        total_students = CandidateProfile.objects.count()

        total_drives = PlacementDrive.objects.count()

        active_drives = PlacementDrive.objects.filter(
            status="OPEN"
        ).count()

        total_applications = Application.objects.count()

        selected_students = Application.objects.filter(
            status__in=[
                "SELECTED",
                "OFFERED",
                "ACCEPTED"
            ]
        ).values("candidate").distinct().count()

        rejected_applications = Application.objects.filter(
            status="REJECTED"
        ).count()

        pending_applications = Application.objects.filter(
            status__in=[
                "APPLIED",
                "UNDER_REVIEW"
            ]
        ).count()

        placement_percentage = (
            round(
                (selected_students / total_students) * 100,
                2
            )
            if total_students else 0
        )

        return Response({
            "total_students": total_students,
            "total_drives": total_drives,
            "active_drives": active_drives,
            "total_applications": total_applications,
            "placed_students": selected_students,
            "unplaced_students": max(
                total_students - selected_students,
                0
            ),
            "rejected_applications": rejected_applications,
            "pending_applications": pending_applications,
            "placement_percentage": placement_percentage,
        })


# =====================================================
# 2. PLACEMENT TRENDS
# GET /api/analytics/placement-trends/
# =====================================================

class PlacementTrendsView(AdminAnalyticsView):

    def get(self, request):

        year = request.query_params.get(
            "year",
            timezone.now().year
        )

        try:
            year = int(year)
        except (TypeError, ValueError):
            return Response(
                {"error": "Invalid year."},
                status=400
            )

        data = (
            ApplicationStatusHistory.objects.filter(
                new_status__in=[
                    "SELECTED",
                    "OFFERED",
                    "ACCEPTED"
                ],
                changed_at__year=year
            )
            .annotate(
                month=TruncMonth("changed_at")
            )
            .values("month")
            .annotate(
                total=Count(
                    "application_id",
                    distinct=True
                )
            )
            .order_by("month")
        )

        return Response([
            {
                "month": item["month"].strftime("%b"),
                "total_placements": item["total"]
            }
            for item in data
        ])


# =====================================================
# 3. APPLICATION TRENDS
# GET /api/analytics/application-trends/
# =====================================================

class ApplicationTrendsView(AdminAnalyticsView):

    def get(self, request):

        year = request.query_params.get(
            "year",
            timezone.now().year
        )

        try:
            year = int(year)
        except (TypeError, ValueError):
            return Response(
                {"error": "Invalid year."},
                status=400
            )

        data = (
            Application.objects.filter(
                applied_at__year=year
            )
            .annotate(
                month=TruncMonth("applied_at")
            )
            .values("month")
            .annotate(
                total=Count("id")
            )
            .order_by("month")
        )

        return Response([
            {
                "month": item["month"].strftime("%b"),
                "total_applications": item["total"]
            }
            for item in data
        ])


# =====================================================
# 4. APPLICATION STATUS ANALYSIS
# GET /api/analytics/application-status/
# =====================================================

class ApplicationStatusView(AdminAnalyticsView):

    def get(self, request):

        data = (
            Application.objects
            .values("status")
            .annotate(
                total=Count("id")
            )
            .order_by("status")
        )

        return Response([
            {
                "status": item["status"],
                "total": item["total"]
            }
            for item in data
        ])


# =====================================================
# 5. DEPARTMENT WISE ANALYTICS
# GET /api/analytics/department-wise/
# =====================================================

class DepartmentWiseAnalyticsView(AdminAnalyticsView):

    def get(self, request):

        data = (
            CandidateProfile.objects
            .values(
                "department_id",
                "department__name"
            )
            .annotate(
                total_students=Count("id", distinct=True),

                placed_students=Count(
                    "id",
                    filter=Q(
                        applications__status__in=[
                            "SELECTED",
                            "OFFERED",
                            "ACCEPTED"
                        ]
                    ),
                    distinct=True
                )
            )
            .order_by("department__name")
        )

        result = []

        for item in data:

            total = item["total_students"]
            placed = item["placed_students"]

            percentage = (
                round((placed / total) * 100, 2)
                if total else 0
            )

            result.append({
                "department_id": item["department_id"],
                "department": item["department__name"],
                "total_students": total,
                "placed_students": placed,
                "unplaced_students": total - placed,
                "placement_percentage": percentage
            })

        return Response(result)


# =====================================================
# 6. COMPANY WISE ANALYTICS
# GET /api/analytics/company-wise/
# =====================================================

class CompanyWiseAnalyticsView(AdminAnalyticsView):

    def get(self, request):

        data = (
            PlacementDrive.objects
            .values(
                "company_id",
                "company__name"
            )
            .annotate(
                total_drives=Count("id"),

                total_applications=Count(
                    "applications",
                    distinct=True
                ),

                selected_candidates=Count(
                    "applications__candidate",
                    filter=Q(
                        applications__status__in=[
                            "SELECTED",
                            "OFFERED",
                            "ACCEPTED"
                        ]
                    ),
                    distinct=True
                )
            )
            .order_by("-selected_candidates")
        )

        return Response([
            {
                "company_id": item["company_id"],
                "company": item["company__name"],
                "total_drives": item["total_drives"],
                "total_applications": item["total_applications"],
                "selected_candidates": item["selected_candidates"]
            }
            for item in data
        ])


# =====================================================
# 7. PACKAGE ANALYSIS
# GET /api/analytics/package-analysis/
# =====================================================

class PackageAnalysisView(AdminAnalyticsView):

    def get(self, request):

        data = PlacementDrive.objects.filter(
            applications__status__in=[
                "SELECTED",
                "OFFERED",
                "ACCEPTED"
            ]
        ).aggregate(
            average_package=Avg("package_max"),
            highest_package=Max("package_max"),
            lowest_package=Min("package_min"),
        )

        return Response({
            "average_package": data["average_package"] or 0,
            "highest_package": data["highest_package"] or 0,
            "lowest_package": data["lowest_package"] or 0,
        })


# =====================================================
# 8. DRIVE PERFORMANCE
# GET /api/analytics/drive-performance/
# =====================================================

class DrivePerformanceView(AdminAnalyticsView):

    def get(self, request):

        data = (
            PlacementDrive.objects
            .annotate(
                total_applications=Count(
                    "applications",
                    distinct=True
                ),

                selected_candidates=Count(
                    "applications__candidate",
                    filter=Q(
                        applications__status__in=[
                            "SELECTED",
                            "OFFERED",
                            "ACCEPTED"
                        ]
                    ),
                    distinct=True
                ),

                rejected_candidates=Count(
                    "applications",
                    filter=Q(
                        applications__status="REJECTED"
                    ),
                    distinct=True
                )
            )
            .order_by("-created_at")
        )

        return Response([
            {
                "drive_id": drive.id,
                "drive_title": drive.title,
                "company": drive.company.name,
                "status": drive.status,
                "openings": drive.openings,
                "total_applications": drive.total_applications,
                "selected_candidates": drive.selected_candidates,
                "rejected_candidates": drive.rejected_candidates,
            }
            for drive in data
        ])


# =====================================================
# 9. INTERVIEW ANALYSIS
# GET /api/analytics/interview-analysis/
# =====================================================

class InterviewAnalysisView(AdminAnalyticsView):

    def get(self, request):

        total_interviews = Interview.objects.count()

        scheduled = Interview.objects.filter(
            status="SCHEDULED"
        ).count()

        completed = Interview.objects.filter(
            status="COMPLETED"
        ).count()

        cancelled = Interview.objects.filter(
            status="CANCELLED"
        ).count()

        passed = Interview.objects.filter(
            result="PASSED"
        ).count()

        failed = Interview.objects.filter(
            result="FAILED"
        ).count()

        on_hold = Interview.objects.filter(
            result="ON_HOLD"
        ).count()

        round_wise = (
            Interview.objects
            .values(
                "interview_round__name",
                "interview_round__round_type"
            )
            .annotate(
                total=Count("id"),
                passed=Count(
                    "id",
                    filter=Q(result="PASSED")
                ),
                failed=Count(
                    "id",
                    filter=Q(result="FAILED")
                )
            )
            .order_by("interview_round__round_number")
        )

        return Response({
            "total_interviews": total_interviews,
            "scheduled": scheduled,
            "completed": completed,
            "cancelled": cancelled,
            "passed": passed,
            "failed": failed,
            "on_hold": on_hold,
            "round_wise": [
                {
                    "round_name": item[
                        "interview_round__name"
                    ],
                    "round_type": item[
                        "interview_round__round_type"
                    ],
                    "total": item["total"],
                    "passed": item["passed"],
                    "failed": item["failed"]
                }
                for item in round_wise
            ]
        })


# =====================================================
# 10. UNPLACED STUDENTS
# GET /api/analytics/unplaced-students/
# =====================================================

class UnplacedStudentsView(AdminAnalyticsView):

    def get(self, request):

        queryset = CandidateProfile.objects.exclude(
            applications__status__in=[
                "SELECTED",
                "OFFERED",
                "ACCEPTED"
            ]
        ).distinct()

        # Department filter
        department = request.query_params.get("department")

        if department:
            queryset = queryset.filter(
                department_id=department
            )

        # Graduation year filter
        graduation_year = request.query_params.get(
            "graduation_year"
        )

        if graduation_year:
            queryset = queryset.filter(
                graduation_year=graduation_year
            )

        # Search filter
        search = request.query_params.get("search")

        if search:
            queryset = queryset.filter(
                Q(user__username__icontains=search) |
                Q(user__first_name__icontains=search) |
                Q(user__last_name__icontains=search) |
                Q(enrollment_number__icontains=search)
            )

        queryset = queryset.select_related(
            "user",
            "department",
            "course"
        ).order_by("user__first_name")

        paginator = PageNumberPagination()
        paginator.page_size = 10

        page = paginator.paginate_queryset(
            queryset,
            request
        )

        result = []

        for student in page:

            result.append({
                "id": student.id,
                "student_name": student.user.get_full_name(),
                "username": student.user.username,
                "email": student.user.email,
                "enrollment_number": student.enrollment_number,
                "department": (
                    student.department.name
                    if student.department else None
                ),
                "course": (
                    student.course.name
                    if student.course else None
                ),
                "graduation_year": student.graduation_year,
                "cgpa": student.current_cgpa,
                "total_applications": student.applications.count()
            })

        return paginator.get_paginated_response(result)
