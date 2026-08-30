# Security Policy

## Commitment

This project is a Flask portfolio website and lightweight micro-CMS. Although the public-facing site is designed for portfolio content, the administration routes, authentication flow, image uploads, email integration, database records, and deployment environment are treated as real security boundaries.

Security work for this repository focuses on protecting:

- administrator authentication and session handling
- admin-only content management routes
- profile, post, project, gallery, and metadata records
- Cloudinary-backed image uploads
- MailerSend contact form delivery
- environment variables, API keys, and deployment secrets
- database migration and deployment integrity

## Supported Versions

Only the current mainline release branch actively receives security updates and vulnerability fixes.

| Version | Supported |
| ------- | --------- |
| Current `main` branch | Supported |
| Older branches or forks | Not actively maintained |

## Reporting a Vulnerability

If you discover a legitimate security vulnerability, please do not open a public GitHub issue or disclose exploit details publicly before a fix is available.

### Reporting Pipeline

1. Email your findings directly to: **tom@deller.co**
2. Include the affected area of the application, such as authentication, admin routes, file uploads, metadata handling, email delivery, database migrations, or deployment configuration.
3. Provide clear reproduction steps and expected impact.
4. Include a concise proof of concept when possible, without using real secrets, real user data, or destructive payloads.

### Response Window

- Acknowledgment: I aim to acknowledge valid reports within 48 hours.
- Triage: I will assess severity, affected versions, and likely remediation steps.
- Remediation: A patch timeline will be coordinated based on severity and exploitability.
- Disclosure: Public disclosure should wait until a fix has been released or a coordinated disclosure date has been agreed.

## In-Scope Security Areas

Reports are especially useful when they relate to:

- authentication bypasses affecting `/login`, `/logout`, `/setup`, or `/edit-profile`
- unauthorized access to admin-only routes protected by `admin_only`
- CSRF bypasses on state-changing forms
- stored or reflected XSS in rich text content, metadata, image captions, tags, or profile fields
- unsafe file upload behavior for profile, hero, gallery, or metadata images
- Cloudinary public ID handling or image deletion abuse
- MailerSend misuse, email header injection, or contact form abuse
- SQL injection or unsafe database query behavior
- migration issues that could corrupt or expose production data
- secrets exposure through `.env`, logs, stack traces, Docker files, or deployment settings
- sitemap, robots, or metadata behavior that unintentionally exposes private/admin pages

## Out-of-Scope Reports

The following are usually out of scope unless they demonstrate a concrete exploit path:

- missing security headers without a working exploit
- automated scanner output without analysis or reproduction steps
- denial-of-service claims based only on generic request flooding
- issues requiring access to an administrator account unless privilege escalation is demonstrated
- vulnerabilities in third-party services where this application is not the cause
- reports against local development files that are not intended for deployment, such as `.venv`, `.idea`, or local SQLite databases

## Application Security Notes

### Authentication and Authorization

The application uses Flask-Login for sessions and Werkzeug password hashing for administrator credentials. Admin-only workflows are protected by the `admin_only` decorator, which requires an authenticated administrator account.

The first administrator is created through `/setup`. Once an administrator exists, setup access is redirected to login.

### CSRF Protection

Flask-WTF CSRF protection is enabled globally. All state-changing forms should include CSRF tokens, including create, edit, delete, upload, setup, login, and metadata forms.

### Secrets and Environment Variables

Secrets must be provided through environment variables and must not be committed to the repository.

Required sensitive values include:

```text
FLASK_SECRET_KEY
CLOUDINARY_CLOUD_NAME
CLOUDINARY_KEY
CLOUDINARY_SECRET
MAILER_API_KEY
MAILER_ADMIN_EMAIL
```

Rotate any credential immediately if it is accidentally committed, leaked in logs, or exposed through a deployment provider.

### Image Uploads

Profile, hero, gallery, and metadata images are uploaded through Cloudinary. The application currently accepts:

```text
jpg
jpeg
png
```

Upload-related reports should include the target route, file type, upload behavior, and whether the issue affects stored URLs, public IDs, deletion, or rendered HTML.

### Rich Text and Stored Content

Posts, projects, profile content, gallery descriptions, and contact messages use rich text fields. Reports involving stored content should clearly identify whether the issue is stored XSS, reflected XSS, unsafe HTML rendering, or content injection through metadata fields.

### Email Handling

The contact form sends mail through MailerSend. Reports should avoid sending abusive test messages. If testing mail behavior, use minimal payloads and clearly mark them as security testing.

### Database and Migrations

The app uses SQLAlchemy and Flask-Migrate/Alembic. Migration reports should include the database engine, migration revision, command run, and observed failure mode.

Production deployments should use a persistent database, such as PostgreSQL, and should run migrations as part of the release process.

## Deployment Security Checklist

Before deploying or merging a production release:

- Confirm `.env` is not committed.
- Set a strong `FLASK_SECRET_KEY` in the deployment environment.
- Confirm Cloudinary and MailerSend keys are present only in the deployment secret store.
- Run database migrations against a staging or backup-safe environment first.
- Confirm admin routes require authentication.
- Confirm upload forms accept only intended image types.
- Confirm `/sitemap.xml` lists only public pages.
- Confirm `/robots.txt` does not accidentally expose private routes.
- Review logs for leaked tokens, stack traces, or personally identifying data.
- Run dependency and package checks before release.

Recommended dependency audit:

```bash
pip-audit
```

If `pip-audit` is not installed:

```bash
pip install pip-audit
pip-audit
```

## Dependency and Supply Chain Security

Dependencies should remain pinned in `requirements.txt` for reproducible deployments. Avoid floating production dependency ranges unless there is a clear maintenance reason.

When upgrading dependencies:

- review changelogs for security and breaking changes
- run the app import and route checks
- run database migration checks
- verify core admin workflows manually before merging

Useful local checks:

```bash
python -m compileall app run.py migrations
flask --app run routes
flask --app run db upgrade
```

## Responsible Testing

Please keep testing non-destructive:

- do not access, alter, delete, or exfiltrate data that is not yours
- do not attempt credential stuffing or brute force attacks
- do not run high-volume automated testing against the live site without permission
- do not upload malicious files to third-party services
- do not publicly disclose vulnerability details before coordination

Good-faith reports that help improve the security of this project are appreciated.
