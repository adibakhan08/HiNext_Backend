
from rest_framework import generics
from rest_framework.permissions import IsAuthenticated
from rest_framework.parsers import MultiPartParser, FormParser

from .models import Company, CompanyContact

from .serializers import (
    CompanySerializer,
    CompanyContactSerializer
)

from .permissions import IsAdminOrReadOnly


# 1. Company List and Create

class CompanyListCreateView(generics.ListCreateAPIView):

    serializer_class = CompanySerializer

    permission_classes = [
        IsAuthenticated,
        IsAdminOrReadOnly
    ]

    parser_classes = [
        MultiPartParser,
        FormParser,
    ]

    def get_queryset(self):

        queryset = Company.objects.prefetch_related('contacts')

        user = self.request.user

        # Students can only see active companies
        if user.role == 'STUDENT':
            queryset = queryset.filter(status='ACTIVE')

        # Search by company name
        search = self.request.query_params.get('search')

        if search:
            queryset = queryset.filter(
                name__icontains=search
            )

        # Filter by industry
        industry = self.request.query_params.get('industry')

        if industry:
            queryset = queryset.filter(
                industry_sector__icontains=industry
            )

        # Filter by status (admin only)
        status_filter = self.request.query_params.get('status')

        if status_filter and user.role == 'ADMIN' and user.is_staff:
            queryset = queryset.filter(status=status_filter)

        return queryset


# 2. Company Retrieve, Update and Delete

class CompanyDetailView(generics.RetrieveUpdateDestroyAPIView):

    serializer_class = CompanySerializer

    permission_classes = [
        IsAuthenticated,
        IsAdminOrReadOnly
    ]

    parser_classes = [
        MultiPartParser,
        FormParser,
    ]

    def get_queryset(self):

        queryset = Company.objects.prefetch_related('contacts')

        user = self.request.user

        if user.role == 'STUDENT':
            queryset = queryset.filter(status='ACTIVE')

        return queryset


# 3. Company Contact List and Create

class CompanyContactListCreateView(generics.ListCreateAPIView):

    serializer_class = CompanyContactSerializer

    permission_classes = [
        IsAuthenticated,
        IsAdminOrReadOnly
    ]

    def get_queryset(self):

        queryset = CompanyContact.objects.select_related('company')

        company_id = self.request.query_params.get('company')

        if company_id:
            queryset = queryset.filter(company_id=company_id)

        return queryset


# 4. Company Contact Retrieve, Update and Delete

class CompanyContactDetailView(generics.RetrieveUpdateDestroyAPIView):

    queryset = CompanyContact.objects.select_related('company')

    serializer_class = CompanyContactSerializer

    permission_classes = [
        IsAuthenticated,
        IsAdminOrReadOnly
    ]
