from django.db import models
from django.conf import settings
from apps.applications.models import Application


class JobOffer(models.Model):

    OFFER_STATUS_CHOICES = [
        ('DRAFT', 'Draft'),
        ('SENT', 'Sent'),
        ('ACCEPTED', 'Accepted'),
        ('REJECTED', 'Rejected'),
        ('EXPIRED', 'Expired'),
        ('WITHDRAWN', 'Withdrawn'),
    ]

    application = models.OneToOneField(
        Application,
        on_delete=models.PROTECT,
        related_name='job_offer'
    )

    job_title = models.CharField(max_length=150)

    annual_ctc = models.DecimalField(
        max_digits=12,
        decimal_places=2
    )

    base_salary = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        null=True,
        blank=True
    )

    joining_date = models.DateField(
        null=True,
        blank=True
    )

    offer_date = models.DateField()

    expiry_date = models.DateField(
        null=True,
        blank=True
    )

    offer_letter = models.FileField(
        upload_to='offers/letters/',
        null=True,
        blank=True
    )

    status = models.CharField(
        max_length=20,
        choices=OFFER_STATUS_CHOICES,
        default='DRAFT'
    )

    remarks = models.TextField(blank=True)

    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name='created_job_offers'
    )

    created_at = models.DateTimeField(auto_now_add=True)

    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.application.candidate} - {self.job_title}"

    class Meta:
        db_table = 'placements_joboffer'
        ordering = ['-created_at']


class Placement(models.Model):

    PLACEMENT_STATUS_CHOICES = [
        ('CONFIRMED', 'Confirmed'),
        ('JOINED', 'Joined'),
        ('NOT_JOINED', 'Not Joined'),
        ('CANCELLED', 'Cancelled'),
    ]

    offer = models.OneToOneField(
        JobOffer,
        on_delete=models.PROTECT,
        related_name='placement'
    )

    candidate = models.ForeignKey(
        'candidates.CandidateProfile',
        on_delete=models.PROTECT,
        related_name='placements'
    )

    company = models.ForeignKey(
        'companies.Company',
        on_delete=models.PROTECT,
        related_name='placements'
    )

    job_title = models.CharField(max_length=150)

    annual_ctc = models.DecimalField(
        max_digits=12,
        decimal_places=2
    )

    joining_date = models.DateField(
        null=True,
        blank=True
    )

    actual_joining_date = models.DateField(
        null=True,
        blank=True
    )

    placement_status = models.CharField(
        max_length=20,
        choices=PLACEMENT_STATUS_CHOICES,
        default='CONFIRMED'
    )

    academic_year = models.CharField(max_length=20)

    remarks = models.TextField(blank=True)

    created_at = models.DateTimeField(auto_now_add=True)

    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.candidate} - {self.company}"

    class Meta:
        db_table = 'placements_placement'
        ordering = ['-created_at']