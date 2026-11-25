
from rest_framework import serializers

from .models import (
    CandidateProfile,
    Education,
    CandidateSkill,
    Resume
)


class CandidateProfileSerializer(serializers.ModelSerializer):

    user = serializers.StringRelatedField(read_only=True)

    class Meta:
        model = CandidateProfile
        fields = '__all__'
        read_only_fields = [
            'id',
            'user',
            'created_at',
            'updated_at',
        ]

    def validate(self, attrs):

        department = attrs.get(
            'department',
            getattr(self.instance, 'department', None)
        )

        course = attrs.get(
            'course',
            getattr(self.instance, 'course', None)
        )

        if department and course and course.department_id != department.id:
            raise serializers.ValidationError({
                'course': 'Selected course does not belong to this department.'
            })

        return attrs


class EducationSerializer(serializers.ModelSerializer):

    class Meta:
        model = Education
        fields = '__all__'
        read_only_fields = ['id', 'candidate', 'created_at']


class CandidateSkillSerializer(serializers.ModelSerializer):

    class Meta:
        model = CandidateSkill
        fields = '__all__'
        read_only_fields = ['id', 'candidate']


class ResumeSerializer(serializers.ModelSerializer):

    class Meta:
        model = Resume
        fields = '__all__'
        read_only_fields = [
            'id',
            'candidate',
            'uploaded_at',
        ]



class AdminCandidateListSerializer(serializers.ModelSerializer):

    username = serializers.CharField(
        source='user.username',
        read_only=True
    )

    first_name = serializers.CharField(
        source='user.first_name',
        read_only=True
    )

    last_name = serializers.CharField(
        source='user.last_name',
        read_only=True
    )

    email = serializers.EmailField(
        source='user.email',
        read_only=True
    )

    phone = serializers.CharField(
        source='user.phone',
        read_only=True
    )

    department_name = serializers.CharField(
        source='department.name',
        read_only=True,
        allow_null=True
    )

    course_name = serializers.CharField(
        source='course.name',
        read_only=True,
        allow_null=True
    )

    class Meta:
        model = CandidateProfile

        fields = [
            'id',
            'user',
            'username',
            'first_name',
            'last_name',
            'email',
            'phone',
            'enrollment_number',
            'profile_photo',
            'department',
            'department_name',
            'course',
            'course_name',
            'graduation_year',
            'current_cgpa',
            'backlogs',
            'created_at',
        ]


class AdminCandidateDetailSerializer(serializers.ModelSerializer):

    username = serializers.CharField(
        source='user.username',
        read_only=True
    )

    first_name = serializers.CharField(
        source='user.first_name',
        read_only=True
    )

    last_name = serializers.CharField(
        source='user.last_name',
        read_only=True
    )

    email = serializers.EmailField(
        source='user.email',
        read_only=True
    )

    phone = serializers.CharField(
        source='user.phone',
        read_only=True
    )

    department_name = serializers.CharField(
        source='department.name',
        read_only=True,
        allow_null=True
    )

    course_name = serializers.CharField(
        source='course.name',
        read_only=True,
        allow_null=True
    )

    education = EducationSerializer(
        many=True,
        read_only=True
    )

    skills = CandidateSkillSerializer(
        source='candidate_skills',
        many=True,
        read_only=True
    )

    resumes = ResumeSerializer(
        many=True,
        read_only=True
    )

    class Meta:
        model = CandidateProfile

        fields = [
            'id',
            'user',
            'username',
            'first_name',
            'last_name',
            'email',
            'phone',
            'enrollment_number',
            'date_of_birth',
            'gender',
            'profile_photo',
            'department',
            'department_name',
            'course',
            'course_name',
            'graduation_year',
            'current_cgpa',
            'backlogs',
            'address',
            'linkedin_url',
            'github_url',
            'portfolio_url',
            'education',
            'skills',
            'resumes',
            'created_at',
            'updated_at'
        ]
