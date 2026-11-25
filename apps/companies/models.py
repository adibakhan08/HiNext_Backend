from django.db import models


class Company(models.Model):

    STATUS_CHOICES = [
        ('ACTIVE', 'Active'),
        ('INACTIVE', 'Inactive'),
        ('BLACKLISTED', 'Blacklisted'),
    ]

    name = models.CharField(max_length=200, unique=True)

    logo = models.ImageField(
        upload_to='companies/logos/',
        null=True,
        blank=True
    )

    website = models.URLField(blank=True)

    description = models.TextField(blank=True)

    industry_sector = models.CharField(
        max_length=150,
        blank=True
    )

    company_size = models.CharField(
        max_length=50,
        blank=True
    )

    headquarters = models.CharField(
        max_length=200,
        blank=True
    )

    address = models.TextField(blank=True)

    email = models.EmailField(blank=True)

    phone = models.CharField(max_length=20, blank=True)

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='ACTIVE'
    )

    created_at = models.DateTimeField(auto_now_add=True)

    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

    class Meta:
        db_table = 'companies_company'
        ordering = ['name']
        verbose_name = 'Company'
        verbose_name_plural = 'Companies'

class CompanyContact(models.Model):

    company = models.ForeignKey(
        Company,
        on_delete=models.CASCADE,
        related_name='contacts'
    )

    name = models.CharField(max_length=150)

    designation = models.CharField(
        max_length=100,
        blank=True
    )

    email = models.EmailField()

    phone = models.CharField(max_length=20)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} - {self.company.name}"

    class Meta:
        db_table = 'companies_companycontact'
        ordering = ['name']