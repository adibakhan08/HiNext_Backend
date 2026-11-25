from django.db import models
from django.conf import settings


class CalendarEvent(models.Model):

    EVENT_TYPE_CHOICES = [
        ('DRIVE', 'Placement Drive'),
        ('INTERVIEW', 'Interview'),
        ('DEADLINE', 'Application Deadline'),
        ('MEETING', 'Meeting'),
        ('OTHER', 'Other'),
    ]

    STATUS_CHOICES = [
        ('UPCOMING', 'Upcoming'),
        ('COMPLETED', 'Completed'),
        ('CANCELLED', 'Cancelled'),
    ]

    title = models.CharField(max_length=200)

    description = models.TextField(blank=True)

    event_type = models.CharField(
        max_length=20,
        choices=EVENT_TYPE_CHOICES
    )

    start_datetime = models.DateTimeField()

    end_datetime = models.DateTimeField()

    location = models.CharField(
        max_length=250,
        blank=True
    )

    meeting_link = models.URLField(blank=True)

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='UPCOMING'
    )

    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name='created_calendar_events'
    )

    attendees = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        related_name='calendar_events',
        blank=True
    )

    created_at = models.DateTimeField(auto_now_add=True)

    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'calendar_calendar_event'
        ordering = ['start_datetime']

    def __str__(self):
        return self.title

    is_auto_generated = models.BooleanField(default=False)
    is_cancelled = models.BooleanField(default=False)
 
    drive = models.ForeignKey(
        'drives.PlacementDrive',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='calendar_events'
    )


class Meta:
    constraints = [
        models.UniqueConstraint(
            fields=['drive', 'event_type'],
            condition=models.Q(
                is_auto_generated=True,
                drive__isnull=False
            ),
            name='unique_auto_drive_event_type'
        )
    ]