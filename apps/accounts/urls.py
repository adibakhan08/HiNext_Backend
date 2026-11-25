from django.urls import path
from .views import LoginView, RegisterView,LogoutView, ProfileView,ChangePasswordView, AdminStudentCreateView

urlpatterns = [
    path(
        'admin/login/',
        LoginView.as_view(),
        {'role': 'ADMIN'}
    ),

    path(
        'user/login/',
        LoginView.as_view(),
        {'role': 'STUDENT'}
    ),
    path('logout/', LogoutView.as_view(), name='logout'),

    path(
    'register/',
    RegisterView.as_view(),
    name='register'
    ),

    path(
        'profile/',
        ProfileView.as_view(),
        name='profile'
    ),

    path(
        'change-password/',
        ChangePasswordView.as_view(),
        name='change-password'
    ),
    path(
        'admin/students/create/',
        AdminStudentCreateView.as_view(),
        name='admin-student-create'
    ),
]