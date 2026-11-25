from django.db import models
from apps.drives.models import PlacementDrive


class InterviewRound(models.Model):

    ROUND_TYPE_CHOICES = [
        ('APTITUDE', 'Aptitude'),
        ('CODING', 'Coding'),
        ('TECHNICAL', 'Technical'),
        ('GROUP_DISCUSSION', 'Group Discussion'),
        ('HR', 'HR'),
        ('MANAGERIAL', 'Managerial'),
        ('OTHER', 'Other'),
    ]

    drive = models.ForeignKey(
        PlacementDrive,
        on_delete=models.CASCADE,
        related_name='interview_rounds'
    )

    name = models.CharField(max_length=150)

    round_type = models.CharField(
        max_length=30,
        choices=ROUND_TYPE_CHOICES
    )

    round_number = models.PositiveIntegerField()

    description = models.TextField(blank=True)

    total_marks = models.PositiveIntegerField(
        null=True,
        blank=True
    )

    is_active = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.drive.title} - {self.name}"

    class Meta:
        db_table = 'interviews_interviewround'
        ordering = ['round_number']

        constraints = [
            models.UniqueConstraint(
                fields=['drive', 'round_number'],
                name='unique_drive_interview_round'
            )
        ]

from apps.applications.models import Application
from django.conf import settings


class Interview(models.Model):

    STATUS_CHOICES = [
        ('SCHEDULED', 'Scheduled'),
        ('COMPLETED', 'Completed'),
        ('CANCELLED', 'Cancelled'),
        ('RESCHEDULED', 'Rescheduled'),
    ]

    RESULT_CHOICES = [
        ('PENDING', 'Pending'),
        ('PASSED', 'Passed'),
        ('FAILED', 'Failed'),
        ('ON_HOLD', 'On Hold'),
    ]

    application = models.ForeignKey(
        Application,
        on_delete=models.CASCADE,
        related_name='interviews'
    )

    interview_round = models.ForeignKey(
        InterviewRound,
        on_delete=models.PROTECT,
        related_name='interviews'
    )

    interviewer = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='conducted_interviews'
    )

    scheduled_at = models.DateTimeField()

    duration_minutes = models.PositiveIntegerField(default=30)

    meeting_link = models.URLField(blank=True)

    location = models.CharField(max_length=200, blank=True)

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='SCHEDULED'
    )

    result = models.CharField(
        max_length=20,
        choices=RESULT_CHOICES,
        default='PENDING'
    )

    score = models.DecimalField(
        max_digits=6,
        decimal_places=2,
        null=True,
        blank=True
    )

    feedback = models.TextField(blank=True)

    remarks = models.TextField(blank=True)

    created_at = models.DateTimeField(auto_now_add=True)

    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.application} - {self.interview_round.name}"

    class Meta:
        db_table = 'interviews_interview'
        ordering = ['scheduled_at']