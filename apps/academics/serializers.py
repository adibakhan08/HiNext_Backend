
from rest_framework import serializers

from .models import (
    Department,
    Course,
    AcademicSession,
    Skill
)


class DepartmentSerializer(serializers.ModelSerializer):

    class Meta:
        model = Department
        fields = '__all__'
        read_only_fields = ['id', 'created_at']


class CourseSerializer(serializers.ModelSerializer):

    department_name = serializers.CharField(
        source='department.name',
        read_only=True
    )

    class Meta:
        model = Course
        fields = '__all__'
        read_only_fields = ['id', 'created_at']


class AcademicSessionSerializer(serializers.ModelSerializer):

    class Meta:
        model = AcademicSession
        fields = '__all__'
        read_only_fields = ['id', 'created_at']

    def validate(self, attrs):

        start_date = attrs.get(
            'start_date',
            getattr(self.instance, 'start_date', None)
        )

        end_date = attrs.get(
            'end_date',
            getattr(self.instance, 'end_date', None)
        )

        if start_date and end_date and start_date >= end_date:
            raise serializers.ValidationError({
                'end_date': 'End date must be after start date.'
            })

        return attrs


class SkillSerializer(serializers.ModelSerializer):

    class Meta:
        model = Skill
        fields = '__all__'
        read_only_fields = ['id', 'created_at']
