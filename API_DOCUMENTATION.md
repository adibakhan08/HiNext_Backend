# HireNext Backend API Documentation

## 1. Project Summary

HireNext is a Django REST Framework placement-management backend for a college or university. It manages users, student profiles, academics, companies, placement drives, applications, and placement workflows.

### Technology

- Django 5.2
- Django REST Framework
- SimpleJWT authentication
- PostgreSQL
- drf-spectacular/OpenAPI support
- CORS support

### Main Modules

| Module | Responsibility |
|---|---|
| `accounts` | Registration, login, logout, profile, password changes, admin-created students |
| `academics` | Departments, courses, academic sessions, and skills |
| `candidates` | Student profiles, education, candidate skills, and resumes |
| `companies` | Company records and company contacts |
| `drives` | Placement drives, eligibility rules, and student registrations |
| `applications` | Student applications and application status history |
| `calendar_app` | Calendar events associated with placement drives |
| `interviews` | Interview rounds, schedules, and evaluations |
| `analytics` | Admin-only placement, application, drive, and interview metrics |

The Django admin is available at `/admin/`. Other installed apps such as placements, notifications, and reports exist in the project, but they do not expose routes in the current root URL configuration.

## 2. Base Configuration

- Base URL: `http://<host>:<port>/`
- API prefix: `/api/`
- Authentication: Bearer JWT
- Default pagination: 10 records per page
- Media files: `/media/<stored-file-path>/`

Example authorization header:

```http
Authorization: Bearer <access_token>
```

JWT access tokens expire after 30 minutes. Refresh tokens expire after one day and are rotated and blacklisted after use.

## Initial Data Setup

The backend includes an idempotent Django seed command for local setup and demonstrations:

```powershell
python manage.py migrate
python manage.py seed_initial_data
```

The command creates or updates initial users and representative records across accounts, academics, candidates, companies, placement drives, applications, interviews, calendar events, notifications, placements, reports, and audit logs. The sample interviews include a scheduled pending interview and a completed, passed interview so the interview analytics endpoint returns non-zero outcome data.

Default development credentials:

| Account | Username | Password |
|---|---|---|
| Admin | `admin` | `Admin@123` |
| Student | `student1` | `Student@123` |
| Student | `student2` | `Student@123` |

Credentials can be overridden before running the command with `SEED_ADMIN_USERNAME`, `SEED_ADMIN_EMAIL`, `SEED_ADMIN_PASSWORD`, and `SEED_STUDENT_PASSWORD`.

```powershell
$env:SEED_ADMIN_USERNAME="placement-admin"
$env:SEED_ADMIN_EMAIL="placement-admin@example.com"
$env:SEED_ADMIN_PASSWORD="StrongAdminPassword123"
$env:SEED_STUDENT_PASSWORD="StrongStudentPassword123"
python manage.py seed_initial_data
```

The seed command may be rerun without creating duplicate model rows where unique or lookup constraints apply. Existing `User`, `Department`, `Course`, `AcademicSession`, `Skill`, `Company`, and candidate/drive/application records are updated with the seed values.

## 3. Authentication and Accounts

### Register a student

```http
POST /api/auth/register/
```

This endpoint is public. It creates a user with the `STUDENT` role.

```json
{
  "username": "student1",
  "email": "student1@example.com",
  "password": "StrongPassword123",
  "confirm_password": "StrongPassword123",
  "first_name": "Asha",
  "last_name": "Sharma",
  "phone": "9876543210"
}
```

### Admin login

```http
POST /api/auth/admin/login/
```

### Student login

```http
POST /api/auth/user/login/
```

Both login endpoints use the same body:

```json
{
  "username": "student1",
  "password": "StrongPassword123"
}
```

A successful response contains `message`, `user`, and `tokens.access`/`tokens.refresh`.

### Refresh access token

```http
POST /api/auth/token/refresh/
Content-Type: application/json
```

```json
{
  "refresh": "<refresh_token>"
}
```

Use this endpoint when a protected API request returns `401` because its access token has expired. The refresh request body uses the refresh token; do not use the expired access token in place of it.

With refresh-token rotation enabled, a successful response contains a new access token and a new refresh token:

```json
{
  "access": "<new_access_token>",
  "refresh": "<new_refresh_token>"
}
```

Replace **both** stored tokens with the returned values, then retry the original request with `Authorization: Bearer <new_access_token>`. The submitted refresh token is blacklisted after rotation and must not be reused. If the refresh token has expired or is invalid, the user must log in again. The refresh endpoint is public and does not require an access-token authorization header.

### Logout

```http
POST /api/auth/logout/
Authorization: Bearer <access_token>
```

```json
{
  "refresh": "<refresh_token>"
}
```

### Get or update the logged-in user's profile

```http
GET /api/auth/profile/
PUT /api/auth/profile/
PATCH /api/auth/profile/
Authorization: Bearer <access_token>
```

Profile fields are `id`, `username`, `email`, `first_name`, `last_name`, `role`, and `phone`.

### Change password

```http
POST /api/auth/change-password/
Authorization: Bearer <access_token>
```

```json
{
  "old_password": "OldPassword123",
  "new_password": "NewPassword456",
  "confirm_password": "NewPassword456"
}
```

### Admin creates a student

```http
POST /api/auth/admin/students/create/
Authorization: Bearer <admin_access_token>
```

```json
{
  "username": "student2",
  "email": "student2@example.com",
  "password": "StrongPassword123",
  "first_name": "Ravi",
  "last_name": "Kumar",
  "phone": "9876501234"
}
```

The caller must have `role=ADMIN` and `is_staff=true`.

## 4. Student Profile APIs

All student APIs require authentication and access the records belonging to the logged-in student. The user must have the `STUDENT` role and must first have a candidate profile where applicable.

### Candidate profile

```http
POST /api/student/profile/create/
GET  /api/student/profile/
PUT  /api/student/profile/
PATCH /api/student/profile/
```

POST creates a profile for the authenticated student. Typical fields:

```json
{
  "enrollment_number": "ENR2026001",
  "date_of_birth": "2004-08-15",
  "gender": "FEMALE",
  "profile_photo": "<profile photo file>",
  "department": 1,
  "course": 1,
  "graduation_year": 2027,
  "current_cgpa": "8.75",
  "backlogs": 0,
  "address": "Pune, Maharashtra",
  "linkedin_url": "https://linkedin.com/in/student",
  "github_url": "https://github.com/student",
  "portfolio_url": "https://student.example.com"
}
```

Gender values are `MALE`, `FEMALE`, and `OTHER`. The selected course must belong to the selected department.

To upload or change `profile_photo`, send the candidate profile request as `multipart/form-data`. JSON and other candidate profile fields can still be updated with `PUT` or `PATCH`.

### Admin candidate APIs

Admins can search and filter candidate profiles without accessing the candidate's student-only education, skill, and resume management endpoints.

```http
GET /api/student/admin/candidates/
GET /api/student/admin/candidates/<id>/
Authorization: Bearer <admin_access_token>
```

The list endpoint supports:

| Parameter | Description | Example |
|---|---|---|
| `search` | Username, first name, last name, email, or enrollment number | `?search=ENR2026001` |
| `department` | Department ID | `?department=1` |
| `course` | Course ID | `?course=1` |
| `graduation_year` | Graduation year | `?graduation_year=2027` |
| `ordering` | `created_at`, `current_cgpa`, `graduation_year`, or `enrollment_number`; prefix with `-` for descending | `?ordering=-current_cgpa` |

The list response includes account and summary fields such as `id`, `user`, `username`, `first_name`, `last_name`, `email`, `phone`, `enrollment_number`, `profile_photo`, `department`, `department_name`, `course`, `course_name`, `graduation_year`, `current_cgpa`, `backlogs`, and `created_at`.

The detail response adds full candidate fields plus nested `education`, `skills`, and `resumes` collections. The nested skills collection contains `skill`, `proficiency_level`, and `years_of_experience`; resumes contain `title`, `resume_file`, and `is_primary`.

### Education

```http
GET    /api/student/education/
POST   /api/student/education/
GET    /api/student/education/<id>/
PUT    /api/student/education/<id>/
PATCH  /api/student/education/<id>/
DELETE /api/student/education/<id>/
```

Create/update body:

```json
{
  "qualification": "Bachelor of Technology",
  "institution": "ABC Institute of Technology",
  "board_or_university": "XYZ University",
  "passing_year": 2027,
  "percentage_or_cgpa": "8.75"
}
```

### Candidate skills

```http
GET    /api/student/skills/
POST   /api/student/skills/
GET    /api/student/skills/<id>/
PUT    /api/student/skills/<id>/
PATCH  /api/student/skills/<id>/
DELETE /api/student/skills/<id>/
```

```json
{
  "skill": 3,
  "proficiency_level": "ADVANCED",
  "years_of_experience": "2.5"
}
```

Proficiency values are `BEGINNER`, `INTERMEDIATE`, `ADVANCED`, and `EXPERT`. A candidate can add each skill only once.

### Resumes

```http
GET    /api/student/resumes/
POST   /api/student/resumes/
GET    /api/student/resumes/<id>/
PUT    /api/student/resumes/<id>/
PATCH  /api/student/resumes/<id>/
DELETE /api/student/resumes/<id>/
```

Use `multipart/form-data` to upload a resume:

```http
Content-Type: multipart/form-data
```

| Field | Type | Description |
|---|---|---|
| `title` | text | Resume title |
| `resume_file` | file | PDF or supported uploaded file |
| `is_primary` | boolean | Mark this resume as primary |

## 5. Academic APIs

These endpoints require authentication. Safe methods are available to authenticated users; create, update, and delete require `role=ADMIN` and `is_staff=true`.

### Departments

```http
GET    /api/academics/departments/
POST   /api/academics/departments/
GET    /api/academics/departments/<id>/
PUT    /api/academics/departments/<id>/
PATCH  /api/academics/departments/<id>/
DELETE /api/academics/departments/<id>/
```

```json
{
  "name": "Computer Science",
  "code": "CSE",
  "description": "Computer science and engineering"
}
```

### Courses

```http
GET    /api/academics/courses/
POST   /api/academics/courses/
GET    /api/academics/courses/<id>/
PUT    /api/academics/courses/<id>/
PATCH  /api/academics/courses/<id>/
DELETE /api/academics/courses/<id>/
```

Filter courses by department:

```http
GET /api/academics/courses/?department=1
```

```json
{
  "name": "B.Tech Computer Science",
  "department": 1,
  "degree_type": "UG",
  "duration_years": 4
}
```

Degree values are `UG`, `PG`, and `DIPLOMA`.

### Academic sessions

```http
GET    /api/academics/sessions/
POST   /api/academics/sessions/
GET    /api/academics/sessions/<id>/
PUT    /api/academics/sessions/<id>/
PATCH  /api/academics/sessions/<id>/
DELETE /api/academics/sessions/<id>/
```

```json
{
  "name": "2026-2027",
  "start_date": "2026-08-01",
  "end_date": "2027-05-31",
  "is_active": true
}
```

The end date must be after the start date.

### Skills

```http
GET    /api/academics/skills/
POST   /api/academics/skills/
GET    /api/academics/skills/<id>/
PUT    /api/academics/skills/<id>/
PATCH  /api/academics/skills/<id>/
DELETE /api/academics/skills/<id>/
```

Filter skills by category:

```http
GET /api/academics/skills/?category=Programming
```

```json
{
  "name": "Python",
  "category": "Programming"
}
```

## 6. Company APIs

These endpoints require authentication. Students can read active companies; only admins can create, update, or delete companies and contacts.

### Companies

```http
GET    /api/companies/
POST   /api/companies/
GET    /api/companies/<id>/
PUT    /api/companies/<id>/
PATCH  /api/companies/<id>/
DELETE /api/companies/<id>/
```

Query parameters:

| Parameter | Applies to | Example |
|---|---|---|
| `search` | Company name | `?search=tech` |
| `industry` | Industry sector | `?industry=software` |
| `status` | Admin only | `?status=ACTIVE` |

The create/update endpoints accept `multipart/form-data`, JSON, or form data:

```json
{
  "name": "Acme Technologies",
  "website": "https://acme.example.com",
  "description": "Software product company",
  "industry_sector": "Software",
  "company_size": "500-1000",
  "headquarters": "Bangalore",
  "address": "Outer Ring Road, Bangalore",
  "email": "hr@acme.example.com",
  "phone": "08012345678",
  "status": "ACTIVE"
}
```

Status values are `ACTIVE`, `INACTIVE`, and `BLACKLISTED`. `logo` can be uploaded as a file.

### Company contacts

```http
GET    /api/companies/contacts/
POST   /api/companies/contacts/
GET    /api/companies/contacts/<id>/
PUT    /api/companies/contacts/<id>/
PATCH  /api/companies/contacts/<id>/
DELETE /api/companies/contacts/<id>/
```

Filter contacts:

```http
GET /api/companies/contacts/?company=1
```

```json
{
  "company": 1,
  "name": "Neha Kapoor",
  "designation": "Talent Acquisition Lead",
  "email": "neha@acme.example.com",
  "phone": "9876543210"
}
```

## 7. Placement Drive APIs

### List or create placement drives

```http
GET  /api/drives/
POST /api/drives/
```

Only admins can create drives. Students can view only currently open drives whose application window is active.

Query parameters:

| Parameter | Description | Example |
|---|---|---|
| `company` | Filter by company ID | `?company=1` |
| `job_type` | `FULL_TIME`, `INTERNSHIP`, or `CONTRACT` | `?job_type=FULL_TIME` |
| `status` | Admin-only status filter | `?status=OPEN` |
| `search` | Search title, role, or company name | `?search=engineer` |

Example create body:

```json
{
  "company": 1,
  "academic_session": 1,
  "title": "Acme Graduate Engineer 2027",
  "job_role": "Software Engineer",
  "job_description": "Build and maintain software products.",
  "job_type": "FULL_TIME",
  "package_min": "600000",
  "package_max": "900000",
  "location": "Bangalore",
  "openings": 25,
  "application_start_date": "2026-11-20T09:00:00Z",
  "application_deadline": "2026-12-10T18:00:00Z",
  "drive_date": "2026-12-20T09:00:00Z",
  "status": "OPEN"
}
```

### Drive detail

```http
GET    /api/drives/<id>/
PUT    /api/drives/<id>/
PATCH  /api/drives/<id>/
DELETE /api/drives/<id>/
```

Status values are `DRAFT`, `UPCOMING`, `OPEN`, `CLOSED`, `COMPLETED`, and `CANCELLED`.

### Drive eligibility

```http
POST  /api/drives/<drive_id>/eligibility/
GET   /api/drives/<drive_id>/eligibility/detail/
PUT   /api/drives/<drive_id>/eligibility/detail/
PATCH /api/drives/<drive_id>/eligibility/detail/
```

Create/update eligibility body:

```json
{
  "minimum_cgpa": "7.50",
  "maximum_backlogs": 1,
  "graduation_year": 2027,
  "eligible_departments": [1],
  "eligible_courses": [1]
}
```

Only admins can manage eligibility. Each course must belong to an eligible department.

### Drive registrations

```http
GET  /api/drives/registrations/
POST /api/drives/registrations/
GET  /api/drives/registrations/<id>/
PUT  /api/drives/registrations/<id>/
PATCH /api/drives/registrations/<id>/
```

Register for a drive:

```json
{
  "drive": 1
}
```

Admin status update body:

```json
{
  "eligibility_status": "ELIGIBLE",
  "registration_status": "REGISTERED"
}
```

Eligibility values are `PENDING`, `ELIGIBLE`, and `NOT_ELIGIBLE`. Registration values are `REGISTERED` and `CANCELLED`.

Admins can filter registrations with:

```http
GET /api/drives/registrations/?drive=1
```

Students can register only after their candidate profile exists, the drive is open and within its application window, openings remain, and they satisfy CGPA, backlog, graduation-year, department, and course rules.

## 8. Calendar APIs

All calendar endpoints require authentication.

### List or create events

```http
GET  /api/calendar/events/
POST /api/calendar/events/
```

Admins (`role=ADMIN` and `is_staff=true`) can list all events and create events. Other authenticated users can list events associated with drives for which they have a registration.

Example create body:

```json
{
  "title": "Acme Technical Interview",
  "description": "Technical interview round",
  "event_type": "INTERVIEW",
  "start_datetime": "2026-12-20T09:00:00Z",
  "end_datetime": "2026-12-20T10:00:00Z",
  "location": "Online",
  "meeting_link": "https://meet.example.com/interview",
  "status": "UPCOMING",
  "attendees": [2, 3],
  "drive": 1
}
```

`event_type` values are `DRIVE`, `INTERVIEW`, `DEADLINE`, `MEETING`, and `OTHER`. `status` values are `UPCOMING`, `COMPLETED`, and `CANCELLED`. `drive` and `attendees` are optional. `created_by` is assigned from the authenticated admin; `is_auto_generated` is read-only.

### Event detail

```http
GET    /api/calendar/events/<id>/
PUT    /api/calendar/events/<id>/
PATCH  /api/calendar/events/<id>/
DELETE /api/calendar/events/<id>/
```

Admins can access any event. Other authenticated users are scoped to events associated with their registered drives. The detail endpoint currently exposes update and delete methods to users who can access an event; only event creation is explicitly admin-only.

The end datetime must not be earlier than the start datetime.

## 9. Interview APIs

All interview endpoints require authentication. Admin access means `role=ADMIN` and `is_staff=true`. Students can read only interviews linked to their own applications. Other authenticated users can read interviews assigned to them as interviewer. Interview round list and detail reads are available to authenticated users.

### Interview rounds

```http
GET    /api/interviews/rounds/
POST   /api/interviews/rounds/
GET    /api/interviews/rounds/<id>/
PUT    /api/interviews/rounds/<id>/
PATCH  /api/interviews/rounds/<id>/
DELETE /api/interviews/rounds/<id>/
```

Only admins can create, update, or delete rounds. Filter rounds by drive:

```http
GET /api/interviews/rounds/?drive=1
```

Example request:

```json
{
  "drive": 1,
  "name": "Technical Interview",
  "round_type": "TECHNICAL",
  "round_number": 1,
  "description": "Technical and coding assessment.",
  "total_marks": 100,
  "is_active": true
}
```

Round types are `APTITUDE`, `CODING`, `TECHNICAL`, `GROUP_DISCUSSION`, `HR`, `MANAGERIAL`, and `OTHER`. A drive cannot have more than one round with the same round number.

### Interviews

```http
GET    /api/interviews/
POST   /api/interviews/
GET    /api/interviews/<id>/
PUT    /api/interviews/<id>/
PATCH  /api/interviews/<id>/
DELETE /api/interviews/<id>/
```

Only admins can schedule, update, or delete interviews. Students and assigned interviewers have read access only through this resource. The list supports these optional filters:

| Parameter | Example |
|---|---|
| `drive` | `?drive=1` |
| `round` | `?round=1` |
| `candidate` | `?candidate=1` |
| `status` | `?status=SCHEDULED` |
| `result` | `?result=PENDING` |

Example schedule request:

```json
{
  "application": 10,
  "interview_round": 1,
  "interviewer": 3,
  "scheduled_at": "2026-12-20T09:00:00Z",
  "duration_minutes": 60,
  "meeting_link": "https://meet.example.com/interview",
  "location": "Online"
}
```

The application must be in `SHORTLISTED` or `INTERVIEW` status, and the selected round must belong to the same drive as the application. Duration must be greater than zero. The server provides interview `status` (initially `SCHEDULED`) and `result` (initially `PENDING`); these fields cannot be set through the schedule/update endpoints.

Interview statuses are `SCHEDULED`, `COMPLETED`, `CANCELLED`, and `RESCHEDULED`. Results are `PENDING`, `PASSED`, `FAILED`, and `ON_HOLD`.

### Submit an interview evaluation

The admin or the interviewer assigned to the interview can submit or update its evaluation:

```http
POST /api/interviews/<id>/result/
Authorization: Bearer <admin_or_assigned_interviewer_access_token>
```

```json
{
  "status": "COMPLETED",
  "result": "PASSED",
  "score": "85.00",
  "feedback": "Strong problem-solving skills.",
  "remarks": "Proceed to the next round."
}
```

Evaluation fields are partial updates. If the round has `total_marks`, `score` cannot exceed it. A final result of `PASSED`, `FAILED`, or `ON_HOLD` can be saved only when the interview status is `COMPLETED`.

## 10. Analytics APIs

All analytics endpoints require authentication and are restricted to users with `role=ADMIN` and `is_staff=true`. These endpoints return aggregate data from existing candidate, drive, application, and interview records; the analytics app does not define its own database models.

### Overview

```http
GET /api/analytics/overview/
```

Returns `total_students`, `total_drives`, `active_drives`, `total_applications`, `placed_students`, `unplaced_students`, `rejected_applications`, `pending_applications`, and `placement_percentage`. A placed student is counted once if they have an application with status `SELECTED`, `OFFERED`, or `ACCEPTED`. Active drives are drives with status `OPEN`; this count does not additionally check the application window.

### Placement and application trends

```http
GET /api/analytics/placement-trends/
GET /api/analytics/application-trends/
```

Both endpoints accept an optional `year` query parameter and default to the current year:

```http
GET /api/analytics/application-trends/?year=2026
```

An invalid year returns `400 Bad Request` with `{"error":"Invalid year."}`. Each endpoint returns an array of month totals, for example:

```json
[
  {
    "month": "Jan",
    "total_applications": 12
  }
]
```

`application-trends` groups applications by their submission date and returns `total_applications`. `placement-trends` groups status-history entries changed during the selected year to `SELECTED`, `OFFERED`, or `ACCEPTED`, counts distinct applications per month, and returns `total_placements`. Months without records are omitted.

### Application status totals

```http
GET /api/analytics/application-status/
```

Returns an array with each recorded application `status` and its `total` count.

### Department and company summaries

```http
GET /api/analytics/department-wise/
GET /api/analytics/company-wise/
```

`department-wise` returns `department_id`, `department`, `total_students`, `placed_students`, `unplaced_students`, and `placement_percentage` per department. `company-wise` returns `company_id`, `company`, `total_drives`, `total_applications`, and `selected_candidates` per company, ordered by selected candidates descending. For these summaries, placed/selected candidates have an application status of `SELECTED`, `OFFERED`, or `ACCEPTED`.

### Package analysis

```http
GET /api/analytics/package-analysis/
```

Returns `average_package`, `highest_package`, and `lowest_package`, aggregated from `package_max`/`package_min` for drives with at least one `SELECTED`, `OFFERED`, or `ACCEPTED` application. Empty aggregate values are returned as `0`.

### Drive performance

```http
GET /api/analytics/drive-performance/
```

Returns one object per drive, newest-created first, with `drive_id`, `drive_title`, `company`, `status`, `openings`, `total_applications`, `selected_candidates`, and `rejected_candidates`.

### Interview analysis

```http
GET /api/analytics/interview-analysis/
```

Returns overall counts `total_interviews`, `scheduled`, `completed`, `cancelled`, `passed`, `failed`, and `on_hold`, plus `round_wise` totals. Each round summary contains `round_name`, `round_type`, `total`, `passed`, and `failed`.

### Unplaced students

```http
GET /api/analytics/unplaced-students/
```

Returns candidates without an application in `SELECTED`, `OFFERED`, or `ACCEPTED` status. This endpoint uses page-number pagination with 10 records per page and supports:

| Parameter | Description | Example |
|---|---|---|
| `department` | Department ID | `?department=2` |
| `graduation_year` | Graduation year | `?graduation_year=2027` |
| `search` | Username, first name, last name, or enrollment number | `?search=ENR2027001` |

Each result contains `id`, `student_name`, `username`, `email`, `enrollment_number`, `department`, `course`, `graduation_year`, `cgpa`, and `total_applications`.

## 11. Application APIs

All application endpoints require authentication. Students can access only their own applications; admins (`role=ADMIN` and `is_staff=true`) can access all applications.

### Available registered drives

```http
GET /api/applications/available-drives/
Authorization: Bearer <student_access_token>
```

Returns the authenticated student's registered drives that are eligible, still registered, open, and within the application window. Only users with `role=STUDENT` can access this endpoint. If the student has no candidate profile, the endpoint returns an empty result list.

The response is a custom `count` and `results` object (not the standard paginated response). Each result includes the registration and drive IDs, drive title, company, job role and type, package range, location, application deadline, registration eligibility/status, and whether the student has already applied. `application_id` and `application_status` are `null` when the student has not applied.

```json
{
  "count": 1,
  "results": [
    {
      "registration_id": 12,
      "drive_id": 1,
      "drive_title": "Acme Graduate Engineer 2027",
      "company_name": "Acme Technologies",
      "job_role": "Software Engineer",
      "job_type": "FULL_TIME",
      "package_min": "600000.00",
      "package_max": "900000.00",
      "location": "Bangalore",
      "application_deadline": "2026-12-10T18:00:00Z",
      "eligibility_status": "ELIGIBLE",
      "registration_status": "REGISTERED",
      "is_applied": false,
      "application_id": null,
      "application_status": null
    }
  ]
}
```

### Track the logged-in student's applications

```http
GET /api/applications/application-tracking/
Authorization: Bearer <student_access_token>
```

This endpoint is for authenticated users with `role=STUDENT` and returns only their applications, newest first. It uses standard page-number pagination. Each application includes drive and company details plus nested `status_history` and `interviews`; it does not include the resume fields returned by the regular application endpoints.

Each tracking result contains `id`, `drive`, `drive_title`, `company_name`, `company_logo`, `job_role`, `job_type`, `location`, `package_min`, `package_max`, `applied_at`, `status`, `current_round`, `remarks`, `updated_at`, `status_history`, and `interviews`. History entries include `id`, `previous_status`, `new_status`, `changed_by_name`, `remarks`, and `changed_at`. Interview entries include `id`, round name/type/number/total marks, schedule and duration, meeting link/location, status, result, score, feedback, and remarks.

```json
{
  "count": 1,
  "next": null,
  "previous": null,
  "results": [
    {
      "id": 10,
      "drive": 1,
      "drive_title": "Acme Graduate Engineer 2027",
      "company_name": "Acme Technologies",
      "company_logo": null,
      "job_role": "Software Engineer",
      "job_type": "FULL_TIME",
      "location": "Bangalore",
      "package_min": "600000.00",
      "package_max": "900000.00",
      "applied_at": "2026-11-22T09:00:00Z",
      "status": "INTERVIEW",
      "current_round": 1,
      "remarks": "Candidate cleared the technical screening.",
      "updated_at": "2026-11-23T09:00:00Z",
      "status_history": [
        {
          "id": 22,
          "previous_status": "APPLIED",
          "new_status": "INTERVIEW",
          "changed_by_name": "admin",
          "remarks": "Candidate cleared the technical screening.",
          "changed_at": "2026-11-23T09:00:00Z"
        }
      ],
      "interviews": [
        {
          "id": 5,
          "round_name": "Technical Interview",
          "round_type": "TECHNICAL",
          "round_number": 1,
          "total_marks": 100,
          "scheduled_at": "2026-12-01T10:00:00Z",
          "duration_minutes": 60,
          "meeting_link": "https://meet.example.com/interview",
          "location": "Online",
          "status": "SCHEDULED",
          "result": "PENDING",
          "score": null,
          "feedback": "",
          "remarks": ""
        }
      ]
    }
  ]
}
```

### List or submit applications

```http
GET  /api/applications/
POST /api/applications/
```

Submit an application as a student with a candidate profile. The request accepts the drive and one of the student's own resumes:

```json
{
  "drive": 1,
  "resume": 2
}
```

The drive must be open and within its application window. The student must have an active, eligible registration for the drive, and can apply only once per drive.

A successful submission returns the application representation:

```json
{
  "id": 10,
  "candidate": 4,
  "candidate_name": "student1",
  "drive": 1,
  "drive_title": "Acme Graduate Engineer 2027",
  "resume": 2,
  "resume_title": "Software Engineer Resume",
  "applied_at": "2026-11-22T09:00:00Z",
  "status": "APPLIED",
  "current_round": 0,
  "remarks": "",
  "updated_at": "2026-11-22T09:00:00Z"
}
```

`candidate`, `status`, `current_round`, and `remarks` are assigned by the server on submission and cannot be set in the create request. A submission also creates the initial status-history entry (`APPLIED`, with the remark `Application submitted.`).

Admins can filter applications by drive, candidate, or status:

```http
GET /api/applications/?drive=1
GET /api/applications/?candidate=1
GET /api/applications/?status=SHORTLISTED
```

### Application detail

```http
GET /api/applications/<id>/
```

### Admin updates application status

```http
PUT  /api/applications/<id>/status/
PATCH /api/applications/<id>/status/
Authorization: Bearer <admin_access_token>
```

```json
{
  "status": "INTERVIEW",
  "current_round": 2,
  "remarks": "Candidate cleared the technical screening."
}
```

The response contains `status`, `current_round`, and `remarks`. Valid status values are:

`APPLIED`, `UNDER_REVIEW`, `SHORTLISTED`, `REJECTED`, `INTERVIEW`, `SELECTED`, `OFFERED`, `ACCEPTED`, `DECLINED`, and `WITHDRAWN`.

An application status-history entry is created when the status changes. Updating only `current_round` or `remarks` does not add a history entry.

### Student withdraws an application

```http
POST /api/applications/<id>/withdraw/
Authorization: Bearer <student_access_token>
```

The response contains a success message, `application_id`, and the updated `status` (`WITHDRAWN`). A history entry is added for the withdrawal. Withdrawal is blocked when the application is already `REJECTED`, `ACCEPTED`, `DECLINED`, `WITHDRAWN`, `OFFERED`, or `SELECTED`.

### Application status history

```http
GET /api/applications/<id>/history/
```

Students can retrieve history only for their own applications. Admins can retrieve history for any application. Each history entry contains `id`, `application`, `previous_status`, `new_status`, `changed_by`, `changed_by_name`, `remarks`, and `changed_at`. The initial submission entry has an empty `previous_status`.

There is no application delete endpoint.

## 12. Pagination and Filtering

List endpoints use DRF page-number pagination.

Example:

```http
GET /api/drives/?page=2
GET /api/academics/courses/?department=1&page=1
```

Typical paginated response:

```json
{
  "count": 25,
  "next": "http://host/api/drives/?page=2",
  "previous": null,
  "results": []
}
```

## 13. Common HTTP Errors

| Status | Typical meaning |
|---|---|
| `400 Bad Request` | Invalid fields, validation failure, or invalid state |
| `401 Unauthorized` | Missing or invalid JWT |
| `403 Forbidden` | Authenticated user lacks role or permission |
| `404 Not Found` | Resource does not exist or is outside the user's scope |

## 14. Common Validation Rules

- Academic session end date must be after start date.
- Candidate course must belong to the candidate department.
- A candidate can only use one own resume in an application.
- A student can apply to a drive only once.
- A student must register and be eligible before applying.
- A drive deadline must be after its application start date.
- Maximum package cannot be lower than minimum package.
- Eligibility courses must belong to eligible departments.
