
from rest_framework import serializers
from apps.interviews.models import InterviewRound, Interview


class InterviewRoundSerializer(serializers.ModelSerializer):

    drive_title = serializers.CharField(
        source="drive.title",
        read_only=True
    )

    class Meta:
        model = InterviewRound
        fields = [
            "id",
            "drive",
            "drive_title",
            "name",
            "round_type",
            "round_number",
            "description",
            "total_marks",
            "is_active",
            "created_at",
        ]
        read_only_fields = ["id", "created_at"]

    def validate(self, attrs):
        drive = attrs.get(
            "drive",
            getattr(self.instance, "drive", None)
        )
        round_number = attrs.get(
            "round_number",
            getattr(self.instance, "round_number", None)
        )

        if drive and round_number:
            qs = InterviewRound.objects.filter(
                drive=drive,
                round_number=round_number
            )

            if self.instance:
                qs = qs.exclude(pk=self.instance.pk)

            if qs.exists():
                raise serializers.ValidationError({
                    "round_number":
                    "This round number already exists for this drive."
                })

        return attrs


class InterviewSerializer(serializers.ModelSerializer):

    drive_id = serializers.IntegerField(
        source="application.drive_id",
        read_only=True
    )

    drive_title = serializers.CharField(
        source="application.drive.title",
        read_only=True
    )

    candidate_name = serializers.SerializerMethodField()

    candidate_email = serializers.SerializerMethodField()

    round_name = serializers.CharField(
        source="interview_round.name",
        read_only=True
    )

    interviewer_name = serializers.SerializerMethodField()

    class Meta:
        model = Interview
        fields = [
            "id",
            "application",
            "drive_id",
            "drive_title",
            "candidate_name",
            "candidate_email",
            "interview_round",
            "round_name",
            "interviewer",
            "interviewer_name",
            "scheduled_at",
            "duration_minutes",
            "meeting_link",
            "location",
            "status",
            "result",
            "score",
            "feedback",
            "remarks",
            "created_at",
            "updated_at",
        ]

        read_only_fields = [
            "id",
            "status",
            "result",
            "score",
            "feedback",
            "created_at",
            "updated_at",
        ]

    def get_candidate_name(self, obj):
        candidate = obj.application.candidate
        user = candidate.user

        return user.get_full_name() or user.username

    def get_candidate_email(self, obj):
        return obj.application.candidate.user.email

    def get_interviewer_name(self, obj):
        if obj.interviewer:
            return (
                obj.interviewer.get_full_name()
                or obj.interviewer.username
            )
        return None

    def validate(self, attrs):
        application = attrs.get(
            "application",
            getattr(self.instance, "application", None)
        )

        interview_round = attrs.get(
            "interview_round",
            getattr(self.instance, "interview_round", None)
        )

        duration = attrs.get(
            "duration_minutes",
            getattr(self.instance, "duration_minutes", 30)
        )

        if application and interview_round:

            if application.drive_id != interview_round.drive_id:
                raise serializers.ValidationError({
                    "interview_round":
                    "The interview round must belong to the application's drive."
                })

            if application.status not in [
                "SHORTLISTED",
                "INTERVIEW"
            ]:
                raise serializers.ValidationError({
                    "application":
                    "Only shortlisted or interview-stage candidates can be scheduled."
                })

        if duration <= 0:
            raise serializers.ValidationError({
                "duration_minutes":
                "Interview duration must be greater than zero."
            })

        return attrs


class InterviewResultSerializer(serializers.ModelSerializer):

    class Meta:
        model = Interview
        fields = [
            "status",
            "result",
            "score",
            "feedback",
            "remarks",
        ]

    def validate(self, attrs):
        interview = self.instance

        result = attrs.get("result", interview.result)
        score = attrs.get("score", interview.score)

        if score is not None:
            total_marks = interview.interview_round.total_marks

            if total_marks is not None and score > total_marks:
                raise serializers.ValidationError({
                    "score":
                    f"Score cannot exceed {total_marks}."
                })

        if result in ["PASSED", "FAILED", "ON_HOLD"]:
            status = attrs.get("status", interview.status)

            if status != "COMPLETED":
                raise serializers.ValidationError({
                    "status":
                    "An interview must be completed before submitting a final result."
                })

        return attrs
