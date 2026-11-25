from django.db import models
from apps.candidates.models import CandidateProfile, Resume
from apps.drives.models import PlacementDrive
from django.conf import settings


class Application(models.Model):

    STATUS_CHOICES = [
        ('APPLIED', 'Applied'),
        ('UNDER_REVIEW', 'Under Review'),
        ('SHORTLISTED', 'Shortlisted'),
        ('REJECTED', 'Rejected'),
        ('INTERVIEW', 'Interview'),
        ('SELECTED', 'Selected'),
        ('OFFERED', 'Offered'),
        ('ACCEPTED', 'Accepted'),
        ('DECLINED', 'Declined'),
        ('WITHDRAWN', 'Withdrawn'),
    ]

    candidate = models.ForeignKey(
        CandidateProfile,
        on_delete=models.PROTECT,
        related_name='applications'
    )

    drive = models.ForeignKey(
        PlacementDrive,
        on_delete=models.PROTECT,
        related_name='applications'
    )

    resume = models.ForeignKey(
        Resume,
        on_delete=models.PROTECT,
        related_name='applications'
    )

    applied_at = models.DateTimeField(auto_now_add=True)

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='APPLIED'
    )

    current_round = models.PositiveIntegerField(default=0)

    remarks = models.TextField(blank=True)

    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'applications_application'

        constraints = [
            models.UniqueConstraint(
                fields=['candidate', 'drive'],
                name='unique_candidate_drive_application'
            )
        ]

        ordering = ['-applied_at']

    def __str__(self):
        return f"{self.candidate} - {self.drive}"


class ApplicationStatusHistory(models.Model):

    application = models.ForeignKey(
        Application,
        on_delete=models.CASCADE,
        related_name='status_history'
    )

    previous_status = models.CharField(
        max_length=20,
        choices=Application.STATUS_CHOICES,
        blank=True
    )

    new_status = models.CharField(
        max_length=20,
        choices=Application.STATUS_CHOICES
    )

    changed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name='application_status_changes'
    )

    remarks = models.TextField(blank=True)

    changed_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'applications_status_history'
        ordering = ['-changed_at']

    def __str__(self):
        return f"{self.application} - {self.new_status}"