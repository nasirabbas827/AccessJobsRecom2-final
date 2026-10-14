# Access Jobs Recom2 Final

AccessJobsRecom2-final is a job portal with profiles, applications, bookmarks, and job discovery.

![Django](https://img.shields.io/badge/Django-2563EB?style=flat-square) ![SQLite](https://img.shields.io/badge/SQLite-0F172A?style=flat-square)

## Overview

The data model covers `JobSeeker`, `Job`, `Bookmark`, `Application`.

## Implemented workflows

The source defines these handlers:

- **Index** — `index`
- **Register** — `register_view`
- **Login** — `login_view`
- **Dashboard** — `dashboard_view`
- **Job Detail** — `job_detail_view`
- **Apply Job** — `apply_job`
- **Toggle Bookmark** — `toggle_bookmark`
- **Bookmarked Jobs** — `bookmarked_jobs`
- **Application Tracking** — `application_tracking`
- **Logout** — `logout_view`
- **Update Profile** — `update_profile_view`

## Getting started

### 1. Get the project

```bash
git clone https://github.com/nasirabbas827/AccessJobsRecom2-final.git
cd AccessJobsRecom2-final
```

### 2. Prepare Python

Create an isolated environment:

```bash
python -m venv .venv
```

Activate it with `.venv\Scripts\activate` on Windows Command Prompt, or `source .venv/bin/activate` on macOS/Linux.

No requirements file is included. The inspected Python imports indicate these dependencies as a starting point:

```bash
python -m pip install Django scikit-learn numpy Pillow
```

Dependency versions are not pinned in this repository.

### 3. Configure and run

Review [`myproject/settings.py`](myproject/settings.py) for database, media, and any email configuration. Use a local copy of the supplied database when available.

```bash
python manage.py migrate
python manage.py runserver
```

Open http://127.0.0.1:8000/. If you need a Django administration account, run `python manage.py createsuperuser`. Application-specific user roles may be managed separately.

## Repository guide

| Path | Purpose |
| --- | --- |
| [`db.sqlite3`](db.sqlite3) | Included SQLite database |
| [`manage.py`](manage.py) | Django command-line entry point |
| [`myapp`](myapp) | Django application modules |
| [`myproject`](myproject) | Django project configuration |
| [`templates`](templates) | HTML page templates |

## Development notes

These setup instructions are based on the repository source. The application has not been executed as part of this documentation update; verify dependencies and configuration in your local environment.
