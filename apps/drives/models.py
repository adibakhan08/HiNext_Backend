from django.db import models
from django.conf import settings
from apps.companies.models import Company
from apps.academics.models import AcademicSession

from apps.academics.models import Department, Course
from apps.candidates.models import CandidateProfile


class PlacementDrive(models.Model):

    STATUS_CHOICES = [
        ('DRAFT', 'Draft'),
        ('UPCOMING', 'Upcoming'),
        ('OPEN', 'Open'),
        ('CLOSED', 'Closed'),
        ('COMPLETED', 'Completed'),
        ('CANCELLED', 'Cancelled'),
    ]

    JOB_TYPE_CHOICES = [
        ('FULL_TIME', 'Full Time'),
        ('INTERNSHIP', 'Internship'),
        ('CONTRACT', 'Contract'),
    ]

    company = models.ForeignKey(
        Company,
        on_delete=models.PROTECT,
        related_name='placement_drives'
    )

    academic_session = models.ForeignKey(
        AcademicSession,
        on_delete=models.PROTECT,
        related_name='placement_drives'
    )

    title = models.CharField(max_length=200)

    job_role = models.CharField(max_length=150)

    job_description = models.TextField()

    job_type = models.CharField(
        max_length=20,
        choices=JOB_TYPE_CHOICES
    )

    package_min = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True
    )

    package_max = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True
    )

    location = models.CharField(max_length=200)

    openings = models.PositiveIntegerField(default=1)

    application_start_date = models.DateTimeField()

    application_deadline = models.DateTimeField()

    drive_date = models.DateTimeField(
        null=True,
        blank=True
    )

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='DRAFT'
    )

    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name='created_drives'
    )

    created_at = models.DateTimeField(auto_now_add=True)

    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.company.name} - {self.job_role}"

    class Meta:
        db_table = 'drives_placementdrive'
        ordering = ['-created_at']


class DriveEligibility(models.Model):

    drive = models.OneToOneField(
        PlacementDrive,
        on_delete=models.CASCADE,
        related_name='eligibility'
    )

    minimum_cgpa = models.DecimalField(
        max_digits=4,
        decimal_places=2,
        default=0
    )

    maximum_backlogs = models.PositiveIntegerField(default=0)

    graduation_year = models.PositiveIntegerField()

    eligible_departments = models.ManyToManyField(
        Department,
        related_name='eligible_drives',
        blank=True
    )

    eligible_courses = models.ManyToManyField(
        Course,
        related_name='eligible_drives',
        blank=True
    )

    def __str__(self):
        return f"Eligibility - {self.drive.title}"

    class Meta:
        db_table = 'drives_driveeligibility'


class DriveRegistration(models.Model):

    ELIGIBILITY_CHOICES = [
        ('PENDING', 'Pending'),
        ('ELIGIBLE', 'Eligible'),
        ('NOT_ELIGIBLE', 'Not Eligible'),
    ]

    STATUS_CHOICES = [
        ('REGISTERED', 'Registered'),
        ('CANCELLED', 'Cancelled'),
    ]

    drive = models.ForeignKey(
        PlacementDrive,
        on_delete=models.CASCADE,
        related_name='registrations'
    )

    candidate = models.ForeignKey(
        CandidateProfile,
        on_delete=models.CASCADE,
        related_name='drive_registrations'
    )

    registered_at = models.DateTimeField(auto_now_add=True)

    eligibility_status = models.CharField(
        max_length=20,
        choices=ELIGIBILITY_CHOICES,
        default='PENDING'
    )

    registration_status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='REGISTERED'
    )

    class Meta:
        db_table = 'drives_driveregistration'

        constraints = [
            models.UniqueConstraint(
                fields=['drive', 'candidate'],
                name='unique_drive_candidate_registration'
            )
        ]

        ordering = ['-registered_at']

    def __str__(self):
        return f"{self.candidate} - {self.drive}"