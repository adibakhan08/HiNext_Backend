from rest_framework import generics
from rest_framework.permissions import IsAuthenticated

from .models import CalendarEvent
from .serializers import CalendarEventSerializer


class CalendarEventListCreateView(generics.ListCreateAPIView):

    serializer_class = CalendarEventSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user

        if user.role == "ADMIN" and user.is_staff:
            return CalendarEvent.objects.all()

        return CalendarEvent.objects.filter(
            drive__registrations__candidate__user=user
        ).distinct()

    def perform_create(self, serializer):
        if self.request.user.role != "ADMIN" or not self.request.user.is_staff:
            from rest_framework.exceptions import PermissionDenied
            raise PermissionDenied("Only admins can create events.")

        serializer.save(created_by=self.request.user)


class CalendarEventDetailView(generics.RetrieveUpdateDestroyAPIView):

    serializer_class = CalendarEventSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user

        if user.role == "ADMIN" and user.is_staff:
            return CalendarEvent.objects.all()

        return CalendarEvent.objects.filter(
            drive__registrations__candidate__user=user
        ).distinct()