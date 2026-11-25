
from rest_framework import serializers

from django.utils import timezone

from .models import (
    PlacementDrive,
    DriveEligibility,
    DriveRegistration
)


class DriveEligibilitySerializer(serializers.ModelSerializer):

    eligible_departments_names = serializers.StringRelatedField(
        source='eligible_departments',
        many=True,
        read_only=True
    )

    eligible_courses_names = serializers.StringRelatedField(
        source='eligible_courses',
        many=True,
        read_only=True
    )

    class Meta:
        model = DriveEligibility
        fields = '__all__'
        read_only_fields = ['id', 'drive']

    def validate(self, attrs):

        departments = attrs.get(
            'eligible_departments',
            self.instance.eligible_departments.all()
            if self.instance else []
        )

        courses = attrs.get(
            'eligible_courses',
            self.instance.eligible_courses.all()
            if self.instance else []
        )

        department_ids = {d.id for d in departments}

        for course in courses:
            if department_ids and course.department_id not in department_ids:
                raise serializers.ValidationError({
                    'eligible_courses':
                    'Every selected course must belong to an eligible department.'
                })

        return attrs


class PlacementDriveSerializer(serializers.ModelSerializer):

    company_name = serializers.CharField(
        source='company.name',
        read_only=True
    )

    academic_session_name = serializers.CharField(
        source='academic_session.name',
        read_only=True
    )

    eligibility = DriveEligibilitySerializer(read_only=True)

    has_applied = serializers.SerializerMethodField()

    registration_status = serializers.SerializerMethodField()

    class Meta:
        model = PlacementDrive
        fields = '__all__'

        read_only_fields = [
            'id',
            'created_by',
            'created_at',
            'updated_at',
        ]

    def get_has_applied(self, obj):

        user = self.context['request'].user

        if user.role != 'STUDENT':
            return None

        return DriveRegistration.objects.filter(
            drive=obj,
            candidate__user=user,
            registration_status='REGISTERED'
        ).exists()

    def get_registration_status(self, obj):

        user = self.context['request'].user

        if user.role != 'STUDENT':
            return None

        registration = DriveRegistration.objects.filter(
            drive=obj,
            candidate__user=user
        ).first()

        return (
            registration.registration_status
            if registration else None
        )

    def to_representation(self, instance):

        data = super().to_representation(instance)

        user = self.context['request'].user

        if user.role != 'STUDENT':
            data.pop('has_applied', None)
            data.pop('registration_status', None)

        return data

    def validate(self, attrs):

        start_date = attrs.get(
            'application_start_date',
            getattr(self.instance, 'application_start_date', None)
        )

        deadline = attrs.get(
            'application_deadline',
            getattr(self.instance, 'application_deadline', None)
        )

        package_min = attrs.get(
            'package_min',
            getattr(self.instance, 'package_min', None)
        )

        package_max = attrs.get(
            'package_max',
            getattr(self.instance, 'package_max', None)
        )

        if start_date and deadline and deadline <= start_date:
            raise serializers.ValidationError({
                'application_deadline':
                'Application deadline must be after the start date.'
            })

        if (
            package_min is not None
            and package_max is not None
            and package_max < package_min
        ):
            raise serializers.ValidationError({
                'package_max':
                'Maximum package cannot be less than minimum package.'
            })

        return attrs


class DriveRegistrationSerializer(serializers.ModelSerializer):

    drive_title = serializers.CharField(
        source='drive.title',
        read_only=True
    )

    candidate_name = serializers.CharField(
        source='candidate.user.username',
        read_only=True
    )

    class Meta:
        model = DriveRegistration
        fields = [
            'id',
            'drive',
            'drive_title',
            'candidate',
            'candidate_name',
            'registered_at',
            'eligibility_status',
            'registration_status',
        ]

        read_only_fields = [
            'id',
            'candidate',
            'registered_at',
            'eligibility_status',
            'registration_status',
        ]


class DriveRegistrationStatusSerializer(serializers.ModelSerializer):

    class Meta:
        model = DriveRegistration
        fields = [
            'eligibility_status',
            'registration_status',
        ]
