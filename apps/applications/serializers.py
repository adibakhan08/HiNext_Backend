
from rest_framework import serializers

from apps.candidates.models import Resume
from apps.drives.models import PlacementDrive, DriveRegistration

from .models import (
    Application,
    ApplicationStatusHistory
)
from apps.interviews.models import Interview


class ApplicationSerializer(serializers.ModelSerializer):

    drive = serializers.PrimaryKeyRelatedField(
        queryset=PlacementDrive.objects.all()
    )

    resume = serializers.PrimaryKeyRelatedField(
        queryset=Resume.objects.all()
    )

    candidate_name = serializers.CharField(
        source='candidate.user.username',
        read_only=True
    )

    drive_title = serializers.CharField(
        source='drive.title',
        read_only=True
    )

    resume_title = serializers.CharField(
        source='resume.title',
        read_only=True
    )

    class Meta:
        model = Application

        fields = [
            'id',
            'candidate',
            'candidate_name',
            'drive',
            'drive_title',
            'resume',
            'resume_title',
            'applied_at',
            'status',
            'current_round',
            'remarks',
            'updated_at',
        ]

        read_only_fields = [
            'id',
            'candidate',
            'candidate_name',
            'drive_title',
            'resume_title',
            'applied_at',
            'status',
            'current_round',
            'remarks',
            'updated_at',
        ]

    def validate(self, attrs):

        request = self.context.get('request')

        if not request:
            return attrs

        user = request.user

        # Resume must belong to logged-in candidate
        resume = attrs.get('resume')

        if resume.candidate.user_id != user.id:
            raise serializers.ValidationError({
                'resume': 'You can only use your own resume.'
            })

        drive = attrs.get('drive')

        # Drive must be open
        from django.utils import timezone

        now = timezone.now()

        if drive.status != 'OPEN':
            raise serializers.ValidationError({
                'drive': 'This placement drive is not open.'
            })

        if now < drive.application_start_date:
            raise serializers.ValidationError({
                'drive': 'Application period has not started.'
            })

        if now > drive.application_deadline:
            raise serializers.ValidationError({
                'drive': 'Application deadline has passed.'
            })

        # Candidate must be registered and eligible
        try:
            registration = DriveRegistration.objects.get(
                drive=drive,
                candidate__user=user
            )

        except DriveRegistration.DoesNotExist:
            raise serializers.ValidationError({
                'drive': 'You must register for this drive before applying.'
            })

        if registration.registration_status != 'REGISTERED':
            raise serializers.ValidationError({
                'drive': 'Your drive registration is not active.'
            })

        if registration.eligibility_status != 'ELIGIBLE':
            raise serializers.ValidationError({
                'drive': 'You are not eligible for this drive.'
            })

        # Prevent duplicate applications
        if Application.objects.filter(
            drive=drive,
            candidate__user=user
        ).exists():

            raise serializers.ValidationError({
                'drive': 'You have already applied for this drive.'
            })

        return attrs


class ApplicationStatusSerializer(serializers.ModelSerializer):

    class Meta:
        model = Application

        fields = [
            'status',
            'current_round',
            'remarks',
        ]


class ApplicationStatusHistorySerializer(serializers.ModelSerializer):

    changed_by_name = serializers.CharField(
        source='changed_by.username',
        read_only=True
    )

    class Meta:
        model = ApplicationStatusHistory

        fields = [
            'id',
            'application',
            'previous_status',
            'new_status',
            'changed_by',
            'changed_by_name',
            'remarks',
            'changed_at',
        ]

        read_only_fields = fields


class ApplicationHistoryTrackingSerializer(
    serializers.ModelSerializer
):

    changed_by_name = serializers.CharField(
        source="changed_by.username",
        read_only=True
    )

    class Meta:
        model = ApplicationStatusHistory

        fields = [
            "id",
            "previous_status",
            "new_status",
            "changed_by_name",
            "remarks",
            "changed_at",
        ]


class InterviewTrackingSerializer(serializers.ModelSerializer):

    round_name = serializers.CharField(
        source="interview_round.name",
        read_only=True
    )

    round_type = serializers.CharField(
        source="interview_round.round_type",
        read_only=True
    )

    round_number = serializers.IntegerField(
        source="interview_round.round_number",
        read_only=True
    )

    total_marks = serializers.IntegerField(
        source="interview_round.total_marks",
        read_only=True
    )

    class Meta:
        model = Interview

        fields = [
            "id",
            "round_name",
            "round_type",
            "round_number",
            "total_marks",
            "scheduled_at",
            "duration_minutes",
            "meeting_link",
            "location",
            "status",
            "result",
            "score",
            "feedback",
            "remarks",
        ]


class ApplicationTrackingSerializer(serializers.ModelSerializer):

    company_name = serializers.CharField(
        source="drive.company.name",
        read_only=True
    )

    company_logo = serializers.ImageField(
        source="drive.company.logo",
        read_only=True
    )

    drive_title = serializers.CharField(
        source="drive.title",
        read_only=True
    )

    job_role = serializers.CharField(
        source="drive.job_role",
        read_only=True
    )

    job_type = serializers.CharField(
        source="drive.job_type",
        read_only=True
    )

    location = serializers.CharField(
        source="drive.location",
        read_only=True
    )

    package_min = serializers.DecimalField(
        source="drive.package_min",
        max_digits=12,
        decimal_places=2,
        read_only=True
    )

    package_max = serializers.DecimalField(
        source="drive.package_max",
        max_digits=12,
        decimal_places=2,
        read_only=True
    )

    status_history = ApplicationHistoryTrackingSerializer(
        many=True,
        read_only=True
    )

    interviews = InterviewTrackingSerializer(
        many=True,
        read_only=True
    )

    class Meta:
        model = Application

        fields = [
            "id",
            "drive",
            "drive_title",
            "company_name",
            "company_logo",
            "job_role",
            "job_type",
            "location",
            "package_min",
            "package_max",
            "applied_at",
            "status",
            "current_round",
            "remarks",
            "updated_at",
            "status_history",
            "interviews",
        ]