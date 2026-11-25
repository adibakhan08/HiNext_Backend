from django.db.models import Count, Avg

from apps.accounts.models import User
from apps.companies.models import Company
from apps.drives.models import PlacementDrive
from apps.applications.models import Application
from apps.placements.models import Placement


def get_dashboard_statistics():

    total_students = User.objects.filter(
        role='STUDENT'
    ).count()

    total_companies = Company.objects.filter(
        status='ACTIVE'
    ).count()

    active_drives = PlacementDrive.objects.filter(
        status='OPEN'
    ).count()

    total_applications = Application.objects.count()

    selected_students = Application.objects.filter(
        status__in=['SELECTED', 'OFFERED', 'ACCEPTED']
    ).values('candidate').distinct().count()

    total_placements = Placement.objects.count()

    average_package = Placement.objects.aggregate(
        average=Avg('annual_ctc')
    )['average'] or 0

    placement_percentage = (
        (total_placements / total_students) * 100
        if total_students else 0
    )

    return {
        'total_students': total_students,
        'total_companies': total_companies,
        'active_drives': active_drives,
        'total_applications': total_applications,
        'selected_students': selected_students,
        'total_placements': total_placements,
        'average_package': round(float(average_package), 2),
        'placement_percentage': round(placement_percentage, 2),
    }