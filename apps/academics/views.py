
from rest_framework import generics
from rest_framework.permissions import IsAuthenticated

from .models import (
    Department,
    Course,
    AcademicSession,
    Skill
)

from .serializers import (
    DepartmentSerializer,
    CourseSerializer,
    AcademicSessionSerializer,
    SkillSerializer
)

from .permissions import IsAdminOrReadOnly


# Department Views

class DepartmentListCreateView(generics.ListCreateAPIView):

    queryset = Department.objects.all()

    serializer_class = DepartmentSerializer

    permission_classes = [
        IsAuthenticated,
        IsAdminOrReadOnly
    ]


class DepartmentDetailView(generics.RetrieveUpdateDestroyAPIView):

    queryset = Department.objects.all()

    serializer_class = DepartmentSerializer

    permission_classes = [
        IsAuthenticated,
        IsAdminOrReadOnly
    ]


# Course Views

class CourseListCreateView(generics.ListCreateAPIView):

    serializer_class = CourseSerializer

    permission_classes = [
        IsAuthenticated,
        IsAdminOrReadOnly
    ]

    def get_queryset(self):

        queryset = Course.objects.select_related('department')

        department_id = self.request.query_params.get(
            'department'
        )

        if department_id:
            queryset = queryset.filter(
                department_id=department_id
            )

        return queryset


class CourseDetailView(generics.RetrieveUpdateDestroyAPIView):

    queryset = Course.objects.select_related('department')

    serializer_class = CourseSerializer

    permission_classes = [
        IsAuthenticated,
        IsAdminOrReadOnly
    ]


# Academic Session Views

class AcademicSessionListCreateView(generics.ListCreateAPIView):

    queryset = AcademicSession.objects.all()

    serializer_class = AcademicSessionSerializer

    permission_classes = [
        IsAuthenticated,
        IsAdminOrReadOnly
    ]


class AcademicSessionDetailView(generics.RetrieveUpdateDestroyAPIView):

    queryset = AcademicSession.objects.all()

    serializer_class = AcademicSessionSerializer

    permission_classes = [
        IsAuthenticated,
        IsAdminOrReadOnly
    ]


# Skill Views

class SkillListCreateView(generics.ListCreateAPIView):

    queryset = Skill.objects.all()

    serializer_class = SkillSerializer

    permission_classes = [
        IsAuthenticated,
        IsAdminOrReadOnly
    ]

    def get_queryset(self):

        queryset = Skill.objects.all()

        category = self.request.query_params.get('category')

        if category:
            queryset = queryset.filter(
                category__iexact=category
            )

        return queryset


class SkillDetailView(generics.RetrieveUpdateDestroyAPIView):

    queryset = Skill.objects.all()

    serializer_class = SkillSerializer

    permission_classes = [
        IsAuthenticated,
        IsAdminOrReadOnly
    ]
