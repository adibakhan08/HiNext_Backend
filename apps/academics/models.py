from django.db import models


class Department(models.Model):

    name = models.CharField(max_length=150, unique=True)
    code = models.CharField(max_length=20, unique=True)
    description = models.TextField(blank=True, null=True)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

    class Meta:
        db_table = 'academics_department'
        ordering = ['name']


class Course(models.Model):

    DEGREE_CHOICES = [
        ('UG', 'Undergraduate'),
        ('PG', 'Postgraduate'),
        ('DIPLOMA', 'Diploma'),
    ]

    name = models.CharField(max_length=150)

    department = models.ForeignKey(
        Department,
        on_delete=models.PROTECT,
        related_name='courses'
    )

    degree_type = models.CharField(
        max_length=20,
        choices=DEGREE_CHOICES
    )

    duration_years = models.PositiveIntegerField()

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

    class Meta:
        db_table = 'academics_course'
        ordering = ['name']
        unique_together = ('name', 'department')

class AcademicSession(models.Model):

    name = models.CharField(max_length=50, unique=True)

    start_date = models.DateField()
    end_date = models.DateField()

    is_active = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

    class Meta:
        db_table = 'academics_academicsession'
        ordering = ['-start_date']


class Skill(models.Model):

    name = models.CharField(
        max_length=100,
        unique=True
    )

    category = models.CharField(
        max_length=100,
        blank=True
    )

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

    class Meta:
        db_table = 'academics_skill'
        ordering = ['name']