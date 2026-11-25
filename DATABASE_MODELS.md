# HireNext Database Models

This document inventories the Django models declared in the HireNext backend and briefly describes the data each model represents. It covers project-defined models; Django's built-in authentication and framework tables are not listed.

## Initial Seed Data

The `seed_initial_data` Django management command creates representative records for local setup and demonstrations. It is idempotent and updates existing seed records identified by stable names or lookup fields.

```powershell
python manage.py migrate
python manage.py seed_initial_data
```

The command creates or updates `User`, `Department`, `Course`, `AcademicSession`, `Skill`, `Company`, `CompanyContact`, `CandidateProfile`, `Education`, `CandidateSkill`, `Resume`, `PlacementDrive`, `DriveEligibility`, `DriveRegistration`, `Application`, `ApplicationStatusHistory`, `InterviewRound`, `Interview`, `CalendarEvent`, `NotificationPreference`, `Notification`, `JobOffer`, `Placement`, `Report`, and `AuditLog` records. Seeded interview data includes a scheduled pending interview and a completed passed interview, providing sample data for interview analytics.

Default seeded accounts:

| Role | Username | Password |
|---|---|---|
| Admin | `admin` | `Admin@123` |
| Student | `student1` | `Student@123` |
| Student | `student2` | `Student@123` |

Admin credentials and the student password can be overridden with `SEED_ADMIN_USERNAME`, `SEED_ADMIN_EMAIL`, `SEED_ADMIN_PASSWORD`, and `SEED_STUDENT_PASSWORD`. Seeded file fields may contain reference paths for resumes and other uploaded files, but they do not upload or create physical media files.

## Accounts

### `User`

The custom account model, based on Django's `AbstractUser`, with a unique email address, role (`ADMIN` or `STUDENT`), phone number, and verification flag.

## Academics

### `Department`

An academic department identified by a unique name and code, with an optional description.

### `Course`

A degree program belonging to a department, with degree type and program duration.

### `AcademicSession`

An academic year or session with start and end dates and an active flag.

### `Skill`

A skill that can be associated with candidate profiles, including an optional category.

## Candidates

### `CandidateProfile`

A student's placement profile linked one-to-one with a user account, containing enrollment, academic, contact, and social-profile information.

### `Education`

A candidate's education history, including qualification, institution, passing year, and result.

### `CandidateSkill`

A candidate's skill record, including proficiency and years of experience. Each candidate can record a given skill only once.

### `Resume`

A resume file uploaded by a candidate, with a title and a flag indicating whether it is the candidate's primary resume.

## Companies

### `Company`

A company profile containing organization, contact, industry, location, logo, and active/blacklisted status information.

### `CompanyContact`

A company contact person with their name, designation, email, and phone number.

## Placement Drives

### `PlacementDrive`

A job or internship opportunity offered by a company for an academic session, including role, package range, openings, dates, and drive status.

### `DriveEligibility`

Eligibility criteria for a placement drive, including minimum CGPA, maximum backlogs, graduation year, and eligible departments and courses.

### `DriveRegistration`

A candidate's registration for a placement drive, including registration time, eligibility result, and registration status.

## Applications

### `Application`

A candidate's application to a placement drive, linked to the resume used and tracking status, current round, remarks, and timestamps. It references a candidate, drive, and resume; those referenced records are protected from deletion while the application exists. A database uniqueness constraint allows each candidate only one application per drive. Application status values are `APPLIED`, `UNDER_REVIEW`, `SHORTLISTED`, `REJECTED`, `INTERVIEW`, `SELECTED`, `OFFERED`, `ACCEPTED`, `DECLINED`, and `WITHDRAWN`.

### `ApplicationStatusHistory`

An audit trail linked to an application, recording previous and new status, the user making the change, remarks, and timestamp. History entries are ordered newest first and are deleted with their application.

## Calendar

### `CalendarEvent`

A scheduled event such as a drive, interview, deadline, meeting, or other event. Events can be linked to a drive, creator, and attendees.

## Interviews

### `InterviewRound`

A named, numbered stage belonging to a placement drive, with a round type, optional maximum marks, description, and active flag. Round numbers are unique within each drive.

### `Interview`

A scheduled interview linked to a candidate application and an interview round, with an optional assigned interviewer, date/time, duration, location or meeting link, status, result, score, feedback, and remarks. The application and interview round must refer to the same drive when scheduled through the API.

## Notifications

### `Notification`

A message delivered to a user, categorized by type and tracked by read status, optional action URL, and timestamps.

### `NotificationPreference`

A user's notification settings for email, application updates, drive announcements, interview reminders, offers, and placement updates.

## Placements and Offers

### `JobOffer`

An offer associated one-to-one with an application, including compensation, dates, offer letter, status, and remarks.

### `Placement`

A candidate's employment placement based on an offer, recording company, job title, compensation, joining dates, academic year, and placement status.

## Reports and Auditing

### `Report`

A generated or requested report, including report type, creator, output file, processing status, and generation time.

### `AuditLog`

A record of a user or system action, including action type, affected model and object, description, optional IP address, and timestamp.

## Apps without declared models

The `analytics` app currently has no project-defined Django models. Its admin-only API endpoints compute aggregate metrics from candidate, placement drive, application, status-history, and interview records.
