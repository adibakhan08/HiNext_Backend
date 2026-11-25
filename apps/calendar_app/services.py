from apps.calendar_app.models import CalendarEvent


def sync_drive_calendar_events(drive, user):

    events = [
        {
            'event_type': 'APPLICATION_OPEN',
            'title': f'{drive.company.name} - Application Window Opens',
            'start_datetime': drive.application_start_date,
            'end_datetime': drive.application_start_date,
        },
        {
            'event_type': 'APPLICATION_DEADLINE',
            'title': f'{drive.company.name} - Last Date to Apply',
            'start_datetime': drive.application_deadline,
            'end_datetime': drive.application_deadline,
        },
        {
            'event_type': 'DRIVE',
            'title': f'{drive.company.name} - {drive.job_role} Recruitment Drive',
            'start_datetime': drive.drive_date,
            'end_datetime': drive.drive_date,
        }
    ]

    for event in events:

        CalendarEvent.objects.update_or_create(

            drive=drive,

            event_type=event['event_type'],

            is_auto_generated=True,

            defaults={
                'title': event['title'],
                'description': drive.job_description,
                'start_datetime': event['start_datetime'],
                'end_datetime': event['end_datetime'],
                'location': drive.location,
                'created_by': user,
                'is_cancelled': drive.status == 'CANCELLED',
            }
        )