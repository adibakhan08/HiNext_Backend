from django.db import models
from django.conf import settings


class Report(models.Model):

    REPORT_TYPE_CHOICES = [
        ('STUDENT', 'Student Report'),
        ('COMPANY', 'Company Report'),
        ('PLACEMENT', 'Placement Report'),
        ('APPLICATION', 'Application Report'),
        ('DRIVE', 'Placement Drive Report'),
        ('INTERVIEW', 'Interview Report'),
        ('CUSTOM', 'Custom Report'),
    ]

    STATUS_CHOICES = [
        ('PENDING', 'Pending'),
        ('PROCESSING', 'Processing'),
        ('COMPLETED', 'Completed'),
        ('FAILED', 'Failed'),
    ]

    title = models.CharField(max_length=200)

    report_type = models.CharField(
        max_length=30,
        choices=REPORT_TYPE_CHOICES
    )

    description = models.TextField(blank=True)

    generated_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name='generated_reports'
    )

    report_file = models.FileField(
        upload_to='reports/',
        null=True,
        blank=True
    )

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='PENDING'
    )

    generated_at = models.DateTimeField(
        null=True,
        blank=True
    )

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'reports_report'
        ordering = ['-created_at']

    def __str__(self):
        return self.title

class AuditLog(models.Model):

    ACTION_CHOICES = [
        ('CREATE', 'Create'),
        ('UPDATE', 'Update'),
        ('DELETE', 'Delete'),
        ('LOGIN', 'Login'),
        ('LOGOUT', 'Logout'),
        ('STATUS_CHANGE', 'Status Change'),
        ('EXPORT', 'Export'),
    ]

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='audit_logs'
    )

    action = models.CharField(
        max_length=30,
        choices=ACTION_CHOICES
    )

    model_name = models.CharField(max_length=100)

    object_id = models.CharField(max_length=100, blank=True)

    description = models.TextField(blank=True)

    ip_address = models.GenericIPAddressField(
        null=True,
        blank=True
    )

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'reports_auditlog'
        ordering = ['-created_at']

        indexes = [
            models.Index(fields=['user', 'created_at']),
            models.Index(fields=['action', 'created_at']),
        ]

    def __str__(self):
        return f"{self.action} - {self.model_name}"