
from django.urls import path

from .views import (
    CompanyListCreateView,
    CompanyDetailView,
    CompanyContactListCreateView,
    CompanyContactDetailView,
)


urlpatterns = [

    # Company APIs
    path(
        '',
        CompanyListCreateView.as_view(),
        name='company-list-create'
    ),

    path(
        '<int:pk>/',
        CompanyDetailView.as_view(),
        name='company-detail'
    ),

    # Company Contact APIs
    path(
        'contacts/',
        CompanyContactListCreateView.as_view(),
        name='company-contact-list-create'
    ),

    path(
        'contacts/<int:pk>/',
        CompanyContactDetailView.as_view(),
        name='company-contact-detail'
    ),

]
