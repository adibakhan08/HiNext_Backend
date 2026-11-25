from django.db import models
from django.conf import settings


class Notification(models.Model):

    TYPE_CHOICES = [
        ('GENERAL', 'General'),
        ('DRIVE', 'Placement Drive'),
        ('APPLICATION', 'Application'),
        ('INTERVIEW', 'Interview'),
        ('OFFER', 'Job Offer'),
        ('PLACEMENT', 'Placement'),
        ('SYSTEM', 'System'),
    ]

    recipient = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='notifications'
    )

    title = models.CharField(max_length=200)

    message = models.TextField()

    notification_type = models.CharField(
        max_length=20,
        choices=TYPE_CHOICES,
        default='GENERAL'
    )

    is_read = models.BooleanField(default=False)

    read_at = models.DateTimeField(
        null=True,
        blank=True
    )

    action_url = models.CharField(
        max_length=500,
        blank=True
    )

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'notifications_notification'
        ordering = ['-created_at']
        indexes = [
            models.Index(
                fields=['recipient', 'is_read']
            ),
            models.Index(
                fields=['-created_at']
            ),
        ]

    def __str__(self):
        return f"{self.title} - {self.recipient}"


class NotificationPreference(models.Model):

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='notification_preferences'
    )

    email_notifications = models.BooleanField(default=True)

    application_updates = models.BooleanField(default=True)

    drive_announcements = models.BooleanField(default=True)

    interview_reminders = models.BooleanField(default=True)

    offer_notifications = models.BooleanField(default=True)

    placement_updates = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True)

    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'notifications_notificationpreference'

    def __str__(self):
        return f"Preferences - {self.user}"