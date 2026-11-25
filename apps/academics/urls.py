
from django.urls import path

from .views import (
    DepartmentListCreateView,
    DepartmentDetailView,
    CourseListCreateView,
    CourseDetailView,
    AcademicSessionListCreateView,
    AcademicSessionDetailView,
    SkillListCreateView,
    SkillDetailView
)


urlpatterns = [

    # Departments
    path(
        'departments/',
        DepartmentListCreateView.as_view(),
        name='department-list-create'
    ),

    path(
        'departments/<int:pk>/',
        DepartmentDetailView.as_view(),
        name='department-detail'
    ),

    # Courses
    path(
        'courses/',
        CourseListCreateView.as_view(),
        name='course-list-create'
    ),

    path(
        'courses/<int:pk>/',
        CourseDetailView.as_view(),
        name='course-detail'
    ),

    # Academic Sessions
    path(
        'sessions/',
        AcademicSessionListCreateView.as_view(),
        name='session-list-create'
    ),

    path(
        'sessions/<int:pk>/',
        AcademicSessionDetailView.as_view(),
        name='session-detail'
    ),

    # Skills
    path(
        'skills/',
        SkillListCreateView.as_view(),
        name='skill-list-create'
    ),

    path(
        'skills/<int:pk>/',
        SkillDetailView.as_view(),
        name='skill-detail'
    ),

]
