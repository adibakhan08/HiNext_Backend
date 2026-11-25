from rest_framework import serializers
from .models import CalendarEvent


class CalendarEventSerializer(serializers.ModelSerializer):

    class Meta:
        model = CalendarEvent
        fields = "__all__"
        read_only_fields = [
            "created_by",
            "is_auto_generated",
        ]

    def validate(self, attrs):

        start = attrs.get(
            "start_datetime",
            getattr(self.instance, "start_datetime", None)
        )

        end = attrs.get(
            "end_datetime",
            getattr(self.instance, "end_datetime", None)
        )

        if start and end and end < start:
            raise serializers.ValidationError(
                "End datetime must be after start datetime."
            )

        return attrs