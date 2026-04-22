# Visitor Management System

A Django and Django REST Framework application for an office receptionist workflow. Visitors register through a public URL, receive a secure QR code, and receptionists use authenticated screens or APIs to look up the QR token, check visitors in, and check them out.

## Stack

- Django 5.1
- Django REST Framework
- Simple JWT plus session authentication
- django-filter
- drf-spectacular Swagger/OpenAPI docs
- qrcode and Pillow
- PostgreSQL preferred through `DATABASE_URL`; SQLite is configured for local development

## Run Locally

```powershell
py -3.11 -m pip install -r requirements.txt
copy .env.example .env
py -3.11 manage.py migrate
py -3.11 manage.py seed_demo
py -3.11 manage.py runserver
```

Demo logins:

- Reception: `reception` / `pass12345`
- Admin: `admin` / `admin12345`

Important URLs:

- Public registration: `http://127.0.0.1:8000/register/`
- Reception login: `http://127.0.0.1:8000/accounts/login/`
- Dashboard: `http://127.0.0.1:8000/reception/`
- QR scanner/lookup: `http://127.0.0.1:8000/reception/scan/`
- Admin: `http://127.0.0.1:8000/admin/`
- API docs: `http://127.0.0.1:8000/api/docs/`

## Database Schema

`accounts.User` extends Django's user model with `full_name` and `role`. Roles are `ADMIN` and `RECEPTIONIST`.

`visitors.Visit` stores visitor, host, schedule, QR, status, and check-in/out information. Indexed fields include `reference_no`, `qr_token`, `status`, `visit_date`, `visitor_phone`, and `host_name`.

`visitors.AuditLog` records critical events: submitted, checked in, and checked out.

## Status Logic

- New registration creates a `PENDING` visit.
- `PENDING` can transition to `CHECKED_IN`.
- `CHECKED_IN` can transition to `CHECKED_OUT`.
- Duplicate check-in, checkout before check-in, and duplicate checkout are blocked server-side.

## API Examples

Register a visit:

```http
POST /api/visits/register/
Content-Type: application/json

{
  "visitor_name": "Jane Visitor",
  "visitor_phone": "+8801711111111",
  "visitor_email": "jane@example.com",
  "visitor_company": "Acme Ltd",
  "purpose_of_visit": "Project meeting",
  "visit_date": "2026-04-23",
  "visit_time": "10:30",
  "host_name": "Sam Host",
  "host_department": "Operations",
  "host_phone": "+8801811111111",
  "host_email": "sam@example.com"
}
```

Authenticate:

```http
POST /api/auth/login/
Content-Type: application/json

{"username": "reception", "password": "pass12345"}
```

Use the returned access token:

```http
Authorization: Bearer <access-token>
```

Lookup QR token:

```http
GET /api/visits/qr/<token>/
```

Check in:

```http
POST /api/visits/<id>/check-in/
```

Check out:

```http
POST /api/visits/<id>/check-out/
```

List and filter:

```http
GET /api/visits/?status=PENDING&visitor_name=Jane&host_name=Sam&date_from=2026-04-01&date_to=2026-04-30
```

Dashboard summary:

```http
GET /api/dashboard/summary/
```

## Production Notes

- Set a strong `DJANGO_SECRET_KEY`.
- Set `DJANGO_DEBUG=False`.
- Use PostgreSQL with `DATABASE_URL=postgres://user:password@host:5432/dbname`.
- Configure `DJANGO_ALLOWED_HOSTS` and `DJANGO_CSRF_TRUSTED_ORIGINS`.
- Serve `MEDIA_ROOT` securely so QR images are available.
- Put Django behind HTTPS and a production WSGI/ASGI server.

## Tests

```powershell
py -3.11 manage.py test apps.accounts apps.visitors
```
