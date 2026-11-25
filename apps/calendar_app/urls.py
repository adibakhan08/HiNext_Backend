from django.urls import path
from .views import (
    CalendarEventListCreateView,
    CalendarEventDetailView,
)

urlpatterns = [
    # List all events / Create event
    path(
        "events/",
        CalendarEventListCreateView.as_view(),
        name="calendar-event-list-create"
    ),

    # Retrieve / Update / Delete event
    path(
        "events/<int:pk>/",
        CalendarEventDetailView.as_view(),
        name="calendar-event-detail"
    ),
]