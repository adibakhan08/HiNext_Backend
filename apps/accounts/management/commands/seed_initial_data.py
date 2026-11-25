import os
from datetime import timedelta

from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.utils import timezone

from apps.academics.models import Department, Course, AcademicSession, Skill
from apps.applications.models import Application, ApplicationStatusHistory
from apps.calendar_app.models import CalendarEvent
from apps.candidates.models import (
    CandidateProfile,
    CandidateSkill,
    Education,
    Resume,
)
from apps.companies.models import Company, CompanyContact
from apps.drives.models import (
    PlacementDrive,
    DriveEligibility,
    DriveRegistration,
)
from apps.interviews.models import InterviewRound, Interview
from apps.notifications.models import Notification, NotificationPreference
from apps.placements.models import JobOffer, Placement
from apps.reports.models import Report, AuditLog


class Command(BaseCommand):
    help = "Creates idempotent initial data for HireNext."

    def handle(self, *args, **options):
        User = get_user_model()

        admin_username = os.getenv("SEED_ADMIN_USERNAME", "admin")
        admin_password = os.getenv("SEED_ADMIN_PASSWORD", "Admin@123")
        student_password = os.getenv("SEED_STUDENT_PASSWORD", "Student@123")

        admin, created = User.objects.get_or_create(
            username=admin_username,
            defaults={
                "email": os.getenv("SEED_ADMIN_EMAIL", "admin@hirenext.local"),
                "role": "ADMIN",
                "is_staff": True,
                "is_superuser": True,
                "is_verified": True,
            },
        )
        admin.email = os.getenv("SEED_ADMIN_EMAIL", "admin@hirenext.local")
        admin.role = "ADMIN"
        admin.is_staff = True
        admin.is_superuser = True
        admin.is_active = True
        admin.is_verified = True
        admin.set_password(admin_password)
        admin.save()

        students = []
        student_defaults = [
            {
                "username": "student1",
                "email": "student1@hirenext.local",
                "first_name": "Asha",
                "last_name": "Sharma",
                "phone": "9876543210",
                "enrollment_number": "ENR2026001",
            },
            {
                "username": "student2",
                "email": "student2@hirenext.local",
                "first_name": "Ravi",
                "last_name": "Kumar",
                "phone": "9876543211",
                "enrollment_number": "ENR2026002",
            },
        ]

        for data in student_defaults:
            student, _ = User.objects.get_or_create(
                username=data["username"],
                defaults={
                    "email": data["email"],
                    "first_name": data["first_name"],
                    "last_name": data["last_name"],
                    "phone": data["phone"],
                    "role": "STUDENT",
                    "is_verified": True,
                },
            )
            student.email = data["email"]
            student.first_name = data["first_name"]
            student.last_name = data["last_name"]
            student.phone = data["phone"]
            student.role = "STUDENT"
            student.is_active = True
            student.is_verified = True
            student.set_password(student_password)
            student.save()
            students.append((student, data))

        cse, _ = Department.objects.get_or_create(
            code="CSE",
            defaults={"name": "Computer Science", "description": "Computer science and engineering"},
        )
        Department.objects.filter(pk=cse.pk).update(
            name="Computer Science",
            description="Computer science and engineering",
        )

        ece, _ = Department.objects.get_or_create(
            code="ECE",
            defaults={"name": "Electronics", "description": "Electronics and communication engineering"},
        )
        Department.objects.filter(pk=ece.pk).update(
            name="Electronics",
            description="Electronics and communication engineering",
        )

        mba, _ = Department.objects.get_or_create(
            code="MBA",
            defaults={"name": "Management", "description": "Business and management studies"},
        )
        Department.objects.filter(pk=mba.pk).update(
            name="Management",
            description="Business and management studies",
        )

        btech, _ = Course.objects.update_or_create(
            name="B.Tech Computer Science",
            department=cse,
            defaults={"degree_type": "UG", "duration_years": 4},
        )
        btech_ece, _ = Course.objects.update_or_create(
            name="B.Tech Electronics",
            department=ece,
            defaults={"degree_type": "UG", "duration_years": 4},
        )
        mba_course, _ = Course.objects.update_or_create(
            name="MBA",
            department=mba,
            defaults={"degree_type": "PG", "duration_years": 2},
        )

        now = timezone.now()
        session, _ = AcademicSession.objects.update_or_create(
            name="2026-2027",
            defaults={
                "start_date": now.date(),
                "end_date": now.date() + timedelta(days=300),
                "is_active": True,
            },
        )
        AcademicSession.objects.exclude(pk=session.pk).update(is_active=False)

        skills = {}
        for name, category in [
            ("Python", "Programming"),
            ("Django", "Framework"),
            ("JavaScript", "Programming"),
            ("React", "Frontend"),
            ("SQL", "Database"),
            ("Communication", "Soft Skills"),
        ]:
            skill, _ = Skill.objects.update_or_create(
                name=name,
                defaults={"category": category},
            )
            skills[name] = skill

        acme, _ = Company.objects.update_or_create(
            name="Acme Technologies",
            defaults={
                "website": "https://acme.example.com",
                "description": "A software product and technology company.",
                "industry_sector": "Software",
                "company_size": "500-1000",
                "headquarters": "Bangalore",
                "address": "Outer Ring Road, Bangalore",
                "email": "hr@acme.example.com",
                "phone": "08012345678",
                "status": "ACTIVE",
            },
        )
        innovex, _ = Company.objects.update_or_create(
            name="Innovex Systems",
            defaults={
                "website": "https://innovex.example.com",
                "description": "A digital engineering and consulting company.",
                "industry_sector": "IT Services",
                "company_size": "1000-5000",
                "headquarters": "Hyderabad",
                "address": "Hitech City, Hyderabad",
                "email": "careers@innovex.example.com",
                "phone": "04012345678",
                "status": "ACTIVE",
            },
        )

        CompanyContact.objects.update_or_create(
            company=acme,
            email="neha@acme.example.com",
            defaults={"name": "Neha Kapoor", "designation": "Talent Acquisition Lead", "phone": "9876501234"},
        )
        CompanyContact.objects.update_or_create(
            company=innovex,
            email="arjun@innovex.example.com",
            defaults={"name": "Arjun Rao", "designation": "Recruitment Manager", "phone": "9876501235"},
        )

        candidates = []
        for index, (student, data) in enumerate(students):
            course = btech if index == 0 else btech_ece
            department = cse if index == 0 else ece
            candidate, _ = CandidateProfile.objects.update_or_create(
                user=student,
                defaults={
                    "enrollment_number": data["enrollment_number"],
                    "date_of_birth": "2004-08-15" if index == 0 else "2004-09-20",
                    "gender": "FEMALE" if index == 0 else "MALE",
                    "department": department,
                    "course": course,
                    "graduation_year": 2027,
                    "current_cgpa": "8.75" if index == 0 else "8.20",
                    "backlogs": 0,
                    "address": "Pune, Maharashtra" if index == 0 else "Nagpur, Maharashtra",
                    "linkedin_url": f"https://linkedin.com/in/{student.username}",
                    "github_url": f"https://github.com/{student.username}",
                    "portfolio_url": f"https://{student.username}.example.com",
                },
            )
            candidates.append(candidate)

            Education.objects.update_or_create(
                candidate=candidate,
                qualification="Bachelor of Technology",
                institution="ABC Institute of Technology",
                defaults={
                    "board_or_university": "XYZ University",
                    "passing_year": 2027,
                    "percentage_or_cgpa": candidate.current_cgpa,
                },
            )
            Resume.objects.update_or_create(
                candidate=candidate,
                title=f"{student.first_name} Software Resume",
                defaults={
                    "resume_file": f"candidates/resumes/{student.username}_resume.pdf",
                    "is_primary": True,
                },
            )

        CandidateSkill.objects.update_or_create(
            candidate=candidates[0],
            skill=skills["Python"],
            defaults={"proficiency_level": "ADVANCED", "years_of_experience": "2.5"},
        )
        CandidateSkill.objects.update_or_create(
            candidate=candidates[0],
            skill=skills["Django"],
            defaults={"proficiency_level": "ADVANCED", "years_of_experience": "1.5"},
        )
        CandidateSkill.objects.update_or_create(
            candidate=candidates[1],
            skill=skills["JavaScript"],
            defaults={"proficiency_level": "INTERMEDIATE", "years_of_experience": "1.0"},
        )

        drive_acme, _ = PlacementDrive.objects.update_or_create(
            company=acme,
            title="Acme Graduate Engineer 2027",
            defaults={
                "academic_session": session,
                "job_role": "Software Engineer",
                "job_description": "Build and maintain software products.",
                "job_type": "FULL_TIME",
                "package_min": "600000",
                "package_max": "900000",
                "location": "Bangalore",
                "openings": 25,
                "application_start_date": now - timedelta(days=1),
                "application_deadline": now + timedelta(days=30),
                "drive_date": now + timedelta(days=45),
                "status": "OPEN",
                "created_by": admin,
            },
        )
        drive_innovex, _ = PlacementDrive.objects.update_or_create(
            company=innovex,
            title="Innovex Technology Analyst 2027",
            defaults={
                "academic_session": session,
                "job_role": "Technology Analyst",
                "job_description": "Work with digital engineering and consulting teams.",
                "job_type": "FULL_TIME",
                "package_min": "450000",
                "package_max": "650000",
                "location": "Hyderabad",
                "openings": 15,
                "application_start_date": now - timedelta(days=1),
                "application_deadline": now + timedelta(days=25),
                "drive_date": now + timedelta(days=40),
                "status": "OPEN",
                "created_by": admin,
            },
        )

        eligibility_acme, _ = DriveEligibility.objects.get_or_create(
            drive=drive_acme,
            defaults={"graduation_year": 2027},
        )
        eligibility_acme.minimum_cgpa = "7.50"
        eligibility_acme.maximum_backlogs = 1
        eligibility_acme.graduation_year = 2027
        eligibility_acme.save()
        eligibility_acme.eligible_departments.set([cse])
        eligibility_acme.eligible_courses.set([btech])

        eligibility_innovex, _ = DriveEligibility.objects.get_or_create(
            drive=drive_innovex,
            defaults={"graduation_year": 2027},
        )
        eligibility_innovex.minimum_cgpa = "7.00"
        eligibility_innovex.maximum_backlogs = 2
        eligibility_innovex.graduation_year = 2027
        eligibility_innovex.save()
        eligibility_innovex.eligible_departments.set([cse, ece])
        eligibility_innovex.eligible_courses.set([btech, btech_ece])

        registrations = []
        for candidate in candidates:
            drive = drive_acme if candidate == candidates[0] else drive_innovex
            registration, _ = DriveRegistration.objects.update_or_create(
                drive=drive,
                candidate=candidate,
                defaults={
                    "eligibility_status": "ELIGIBLE",
                    "registration_status": "REGISTERED",
                },
            )
            registrations.append(registration)

        candidate_a_resume = Resume.objects.get(candidate=candidates[0], is_primary=True)
        application, _ = Application.objects.update_or_create(
            candidate=candidates[0],
            drive=drive_acme,
            defaults={
                "resume": candidate_a_resume,
                "status": "INTERVIEW",
                "current_round": 1,
                "remarks": "Candidate cleared the initial screening.",
            },
        )
        ApplicationStatusHistory.objects.get_or_create(
            application=application,
            previous_status="",
            new_status="APPLIED",
            changed_by=students[0][0],
            defaults={"remarks": "Application submitted."},
        )
        ApplicationStatusHistory.objects.get_or_create(
            application=application,
            previous_status="APPLIED",
            new_status="INTERVIEW",
            changed_by=admin,
            defaults={
                "remarks": "Candidate cleared the initial screening.",
            },
        )

        round_one, _ = InterviewRound.objects.update_or_create(
            drive=drive_acme,
            round_number=1,
            defaults={
                "name": "Technical Interview",
                "round_type": "TECHNICAL",
                "description": "Technical and coding assessment.",
                "total_marks": 100,
                "is_active": True,
            },
        )
        Interview.objects.update_or_create(
            application=application,
            interview_round=round_one,
            defaults={
                "interviewer": admin,
                "scheduled_at": now + timedelta(days=5),
                "duration_minutes": 60,
                "meeting_link": "https://meet.example.com/acme-technical",
                "location": "",
                "status": "SCHEDULED",
                "result": "PENDING",
            },
        )

        innovex_round, _ = InterviewRound.objects.update_or_create(
            drive=drive_innovex,
            round_number=1,
            defaults={
                "name": "Final Technical Interview",
                "round_type": "TECHNICAL",
                "description": "Final technical assessment.",
                "total_marks": 100,
                "is_active": True,
            },
        )

        for drive in [drive_acme, drive_innovex]:
            event, _ = CalendarEvent.objects.update_or_create(
                title=f"{drive.title} - Application Deadline",
                defaults={
                    "description": "Application deadline for the placement drive.",
                    "event_type": "DEADLINE",
                    "start_datetime": drive.application_deadline,
                    "end_datetime": drive.application_deadline + timedelta(hours=1),
                    "location": "Online",
                    "meeting_link": "",
                    "status": "UPCOMING",
                    "created_by": admin,
                    "is_auto_generated": True,
                    "is_cancelled": False,
                    "drive": drive,
                },
            )
            event.attendees.set([candidate.user for candidate in candidates if candidate.drive_registrations.filter(drive=drive).exists()])

        selected_application, _ = Application.objects.update_or_create(
            candidate=candidates[1],
            drive=drive_innovex,
            defaults={
                "resume": Resume.objects.get(candidate=candidates[1], is_primary=True),
                "status": "OFFERED",
                "current_round": 2,
                "remarks": "Offer process initiated.",
            },
        )
        Interview.objects.update_or_create(
            application=selected_application,
            interview_round=innovex_round,
            defaults={
                "interviewer": admin,
                "scheduled_at": now - timedelta(days=2),
                "duration_minutes": 60,
                "meeting_link": "https://meet.example.com/innovex-technical",
                "location": "",
                "status": "COMPLETED",
                "result": "PASSED",
                "score": "88.00",
                "feedback": "Strong technical performance.",
                "remarks": "Recommended for offer.",
            },
        )

        for student, _ in students:
            NotificationPreference.objects.update_or_create(
                user=student,
                defaults={
                    "email_notifications": True,
                    "application_updates": True,
                    "drive_announcements": True,
                    "interview_reminders": True,
                    "offer_notifications": True,
                    "placement_updates": True,
                },
            )
            Notification.objects.get_or_create(
                recipient=student,
                title="Welcome to HireNext",
                message="Your student account is ready. Complete your profile and explore placement drives.",
                notification_type="SYSTEM",
                defaults={"action_url": "/profile"},
            )

        ApplicationStatusHistory.objects.get_or_create(
            application=selected_application,
            previous_status="",
            new_status="APPLIED",
            changed_by=candidates[1].user,
            defaults={"remarks": "Application submitted."},
        )
        ApplicationStatusHistory.objects.get_or_create(
            application=selected_application,
            previous_status="APPLIED",
            new_status="OFFERED",
            changed_by=admin,
            defaults={"remarks": "Offer process initiated."},
        )

        candidate_b_registration = registrations[1]
        DriveRegistration.objects.filter(pk=candidate_b_registration.pk).update(
            eligibility_status="ELIGIBLE",
            registration_status="REGISTERED",
        )

        offer, _ = JobOffer.objects.update_or_create(
            application=selected_application,
            defaults={
                "job_title": "Technology Analyst",
                "annual_ctc": "550000",
                "base_salary": "500000",
                "joining_date": now.date() + timedelta(days=240),
                "offer_date": now.date(),
                "expiry_date": now.date() + timedelta(days=21),
                "status": "SENT",
                "remarks": "Initial offer generated.",
                "created_by": admin,
            },
        )
        Placement.objects.update_or_create(
            offer=offer,
            defaults={
                "candidate": candidates[1],
                "company": innovex,
                "job_title": "Technology Analyst",
                "annual_ctc": "550000",
                "joining_date": now.date() + timedelta(days=240),
                "placement_status": "CONFIRMED",
                "academic_year": "2026-2027",
                "remarks": "Placement offer confirmed.",
            },
        )

        Report.objects.get_or_create(
            title="Initial Placement Summary",
            report_type="PLACEMENT",
            generated_by=admin,
            defaults={
                "description": "Seeded summary report for initial project setup.",
                "status": "COMPLETED",
                "generated_at": now,
            },
        )
        AuditLog.objects.get_or_create(
            user=admin,
            action="CREATE",
            model_name="seed_initial_data",
            object_id="initial",
            defaults={
                "description": "Initial application data seeded.",
                "ip_address": "127.0.0.1",
            },
        )

        self.stdout.write(self.style.SUCCESS("Initial HireNext data seeded successfully."))
        self.stdout.write(
            f"Admin credentials: username={admin_username}, "
            f"password={admin_password}"
        )
        self.stdout.write(
            f"Student credentials: student1/student2, "
            f"password={student_password}"
        )
