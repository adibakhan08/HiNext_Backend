from django.db import models
from apps.accounts.models import User
from apps.academics.models import Department, Course

from apps.academics.models import Skill


class CandidateProfile(models.Model):

    GENDER_CHOICES = [
        ('MALE', 'Male'),
        ('FEMALE', 'Female'),
        ('OTHER', 'Other'),
    ]

    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='candidate_profile'
    )

    enrollment_number = models.CharField(
        max_length=50,
        unique=True,
        blank=True,
        null=True
    )

    date_of_birth = models.DateField(
        null=True,
        blank=True
    )

    gender = models.CharField(
        max_length=10,
        choices=GENDER_CHOICES,
        blank=True
    )

    profile_photo = models.ImageField(
        upload_to='candidates/profile/',
        null=True,
        blank=True
    )

    department = models.ForeignKey(
        Department,
        on_delete=models.PROTECT,
        related_name='candidates',
        null=True,
        blank=True
    )


    course = models.ForeignKey(
        Course,
        on_delete=models.PROTECT,
        related_name='candidates',
        null=True,
        blank=True
    )


    graduation_year = models.PositiveIntegerField(
        null=True,
        blank=True
    )

    current_cgpa = models.DecimalField(
        max_digits=4,
        decimal_places=2,
        null=True,
        blank=True
    )

    backlogs = models.PositiveIntegerField(default=0)

    address = models.TextField(blank=True)

    linkedin_url = models.URLField(blank=True)
    github_url = models.URLField(blank=True)
    portfolio_url = models.URLField(blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.username} - {self.enrollment_number}"

    class Meta:
        db_table = 'candidates_candidateprofile'
        ordering = ['enrollment_number']


class Education(models.Model):

    candidate = models.ForeignKey(
        CandidateProfile,
        on_delete=models.CASCADE,
        related_name='education'
    )

    qualification = models.CharField(max_length=100)

    institution = models.CharField(max_length=200)

    board_or_university = models.CharField(max_length=200)

    passing_year = models.PositiveIntegerField()

    percentage_or_cgpa = models.DecimalField(
        max_digits=6,
        decimal_places=2
    )

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.candidate.user.username} - {self.qualification}"

    class Meta:
        db_table = 'candidates_education'
        ordering = ['-passing_year']


class CandidateSkill(models.Model):

    PROFICIENCY_CHOICES = [
        ('BEGINNER', 'Beginner'),
        ('INTERMEDIATE', 'Intermediate'),
        ('ADVANCED', 'Advanced'),
        ('EXPERT', 'Expert'),
    ]

    candidate = models.ForeignKey(
        CandidateProfile,
        on_delete=models.CASCADE,
        related_name='candidate_skills'
    )

    skill = models.ForeignKey(
        Skill,
        on_delete=models.CASCADE,
        related_name='candidate_skills'
    )

    proficiency_level = models.CharField(
        max_length=20,
        choices=PROFICIENCY_CHOICES
    )

    years_of_experience = models.DecimalField(
        max_digits=4,
        decimal_places=1,
        default=0
    )

    class Meta:
        db_table = 'candidates_candidateskill'
        constraints = [
            models.UniqueConstraint(
                fields=['candidate', 'skill'],
                name='unique_candidate_skill'
            )
        ]

    def __str__(self):
        return f"{self.candidate} - {self.skill}"


class Resume(models.Model):

    candidate = models.ForeignKey(
        CandidateProfile,
        on_delete=models.CASCADE,
        related_name='resumes'
    )

    title = models.CharField(max_length=150)

    resume_file = models.FileField(
        upload_to='candidates/resumes/'
    )

    is_primary = models.BooleanField(default=False)

    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.candidate} - {self.title}"

    class Meta:
        db_table = 'candidates_resume'
        ordering = ['-uploaded_at']