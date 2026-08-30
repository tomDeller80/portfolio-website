# Flask Portfolio & Micro-CMS

[![GitHub release](https://img.shields.io/github/v/release/tomDeller80/portfolio-website)](https://github.com/tomDeller80/portfolio-website/releases)
[![Python](https://img.shields.io/badge/python-3.11+-3776ab?logo=python&logoColor=white)](requirements.txt)
[![Flask](https://img.shields.io/badge/flask-3.1+-000000?logo=flask&logoColor=white)](requirements.txt)
[![Docker](https://img.shields.io/badge/docker-ready-2496ed?logo=docker&logoColor=white)](Dockerfile)
[![License](https://img.shields.io/badge/license-MIT-green)](LICENSE)
[![Security](https://img.shields.io/badge/security-policy-critical)](SECURITY.md)

A bespoke portfolio website and lightweight content management system built with Python and Flask.

The application lets an authenticated administrator manage portfolio content directly from the live site. Posts, projects, skills, profile information, page metadata, and images are all managed through contextual admin screens rather than a separate admin backend.

## Key Features

- Dynamic posts and projects with create, edit, and delete workflows.
- First-run setup flow for creating the administrator profile.
- In-place admin controls for authenticated administrators.
- Profile management for the site owner's name, role, bio, location, social links, profile image URL/upload, and resume URL.
- Skill and technology badge management.
- Rich text editing with Flask-Quill and Quill.js.
- Cloudinary-backed profile image, hero image, gallery image, and social preview image uploads.
- Ordered galleries for posts and projects.
- SEO metadata management for static and listing pages.
- Automatic metadata for post and project detail pages.
- Sitemap and robots support with per-page indexing controls.
- Contact form delivery through MailerSend.
- Bootstrap 5, Jinja2 templates, and custom CSS.
- Docker, Docker Compose, Gunicorn, and Render-compatible deployment files.

## Tech Stack

- Backend: Python, Flask
- Database: SQLite by default, PostgreSQL-ready for production
- ORM: SQLAlchemy with Flask-SQLAlchemy
- Migrations: Flask-Migrate and Alembic
- Authentication: Flask-Login and Werkzeug password hashing
- Forms: Flask-WTF and WTForms
- Frontend: Bootstrap-Flask, Jinja2, custom CSS
- Rich text: Flask-Quill / Quill.js
- Media storage: Cloudinary
- Email: MailerSend
- Assets: Flask-Assets / Webassets with `rcssmin`
- Production server: Gunicorn

## Project Structure

```text
PortfolioWebsite/
|-- app/
|   |-- routes/
|   |   |-- auth.py
|   |   |-- main.py
|   |   |-- media.py
|   |   |-- posts.py
|   |   |-- projects.py
|   |   `-- sitemap.py
|   |-- services/
|   |   |-- cloudinary_service.py
|   |   `-- mailer_service.py
|   |-- static/
|   |   |-- css/
|   |   |-- ico/
|   |   |-- img/
|   |   `-- robots.txt
|   |-- templates/
|   |-- __init__.py
|   |-- assets.py
|   |-- config.py
|   |-- context_processors.py
|   |-- database.py
|   |-- decorators.py
|   |-- extensions.py
|   |-- forms.py
|   |-- helpers.py
|   |-- hooks.py
|   `-- logger.py
|-- instance/
|-- migrations/
|-- Dockerfile
|-- docker-compose.yml
|-- Procfile
|-- requirements.txt
`-- run.py
```

## Installation

Clone the repository:

```bash
git clone https://github.com/tomDeller80/portfolio-website.git
cd portfolio-website
```

Create and activate a virtual environment:

```bash
python -m venv .venv
.venv\Scripts\activate
```

Install dependencies:

```bash
pip install -r requirements.txt
```

## Environment Variables

Copy `.env.example` to `.env` for local development, or set the same variables in your deployment environment.

```bash
FLASK_SECRET_KEY=your_secret_key_here
DATABASE_URL=sqlite:///portfolio.db
CLOUDINARY_CLOUD_NAME=your_cloud_name
CLOUDINARY_KEY=your_key
CLOUDINARY_SECRET=your_secret
MAILER_ADMIN_NAME=Admin
MAILER_ADMIN_EMAIL=admin@example.com
MAILER_API_KEY=your_mailer_key
SITE_LASTMOD=2026-08-16
```

Notes:

- `DATABASE_URL` falls back to `sqlite:///portfolio.db` if it is not set.
- Docker Compose overrides the app database URL with `DOCKER_DATABASE_URL` when that variable is provided, otherwise it uses a persisted SQLite database at `/app/instance/portfolio.db`.
- `SITE_LASTMOD` controls the default sitemap last-modified date for static routes. If it is omitted, the app uses the current date.
- Cloudinary uploads require `CLOUDINARY_CLOUD_NAME`, `CLOUDINARY_KEY`, and `CLOUDINARY_SECRET`.
- The contact form requires `MAILER_ADMIN_NAME`, `MAILER_ADMIN_EMAIL`, and `MAILER_API_KEY`.

## Database Setup

Apply existing migrations:

```bash
flask --app run db upgrade
```

When changing database models, create and apply a migration:

```bash
flask --app run db migrate -m "describe your change"
flask --app run db upgrade
```

The first-run setup route can also create the initial tables if the users table does not exist, but migrations are the preferred path for an existing deployment.

## Running Locally

Start the application:

```bash
python run.py
```

Then open:

```text
http://127.0.0.1:5000
```

On first launch, if no admin user exists, the app redirects to:

```text
/setup
```

After setup, log in at:

```text
/login
```

## Initial Setup

The setup page creates the first administrator account and captures profile information used throughout the site:

- display name
- email and password
- job title, pronoun, and tagline
- about/profile content
- location
- LinkedIn and GitHub URLs
- profile image URL or uploaded profile image
- resume URL

Once an admin account exists, visiting `/setup` redirects to `/login`.

## Admin Workflow

Authenticated administrators can:

- edit their profile at `/edit-profile`
- create, edit, and delete posts
- create, edit, and delete projects
- upload or replace post and project hero images
- upload and delete post and project gallery images
- add and remove skills/technology badges
- add or update page metadata
- control whether managed pages should be indexed

Admin-only pages and minimal admin templates are intended to stay out of search indexes.

## Content Routes

Public routes include:

```text
/
/about
/contact
/posts
/posts/<page>
/post/<post_id>
/post/<post_id>/<slug>
/projects
/projects/<page>
/project/<project_id>
/project/<project_id>/<slug>
/sitemap.xml
/robots.txt
```

Admin routes include:

```text
/setup
/login
/logout
/edit-profile
/new-post
/edit-post/<post_id>
/delete-post/<post_id>
/new-project
/edit-project/<project_id>
/delete-project/<project_id>
/add-skill
/delete-skill/<skill_id>
/add-meta
/upload/<target_type>/<target_id>
/delete-image/<target_type>/<target_id>/<public_id>
```

## SEO and Metadata

The site stores database-managed metadata for static and listing pages such as:

- Home
- About
- Contact
- Posts listing
- Projects listing

Metadata records are stored against Flask endpoint names, for example:

```text
main.home
main.about
main.contact
posts.get_all_posts
projects.get_all_projects
```

Administrators should open metadata editing from the page's Add Metadata control so the current endpoint is passed automatically.

Each metadata record supports:

- meta title
- meta description
- social preview image URL
- uploaded social preview image
- Open Graph type
- search indexing control

Post and project detail pages generate metadata from their database records.

The application also exposes crawler support files:

```text
/sitemap.xml
/robots.txt
```

`/sitemap.xml` is generated from registered public routes, including post and project detail pages. `/robots.txt` is served from `app/static/robots.txt`, while page-level robots metadata is controlled by each page's metadata record.

## Media Management

Image uploads support `jpg`, `jpeg`, and `png` files.

Administrators can upload and manage images for:

- post hero images
- project hero images
- post galleries
- project galleries
- profile images
- metadata/social preview images

Cloudinary stores the uploaded image files. The application stores secure URLs and, for gallery images, Cloudinary public IDs for deletion.

## Docker

Build the image:

```bash
docker build -t portfolio-website .
```

Run the container:

```bash
docker run --env-file .env -p 5000:5000 portfolio-website
```

Or use Docker Compose:

```bash
docker compose up --build
```

Stop the Compose stack:

```bash
docker compose down
```

The Compose setup persists the SQLite database in the `db_data` volume.

## Deployment

The project can be deployed to Render or another WSGI-compatible host.

Build command:

```bash
pip install -r requirements.txt
```

Start command:

```bash
gunicorn run:app
```

For production:

- set all required environment variables in the hosting provider
- use a persistent database such as PostgreSQL
- set `DATABASE_URL` to the production database connection string
- run `flask --app run db upgrade` after deploying migrations

## Troubleshooting

### First run redirects to setup

This is expected when no administrator exists. Complete the setup form at `/setup`.

### Metadata does not appear on a page

Check that:

- the page has a `PageMeta` record
- the stored endpoint matches the Flask endpoint
- the page extends `base.html`
- post and project detail routes pass their own metadata values

### Add Metadata form does not save

Open the metadata form from the page's Add Metadata control instead of visiting `/add-meta` directly. The control passes the current endpoint automatically.

### Image uploads fail

Check that:

- `CLOUDINARY_CLOUD_NAME`, `CLOUDINARY_KEY`, and `CLOUDINARY_SECRET` are set
- the uploaded file is `jpg`, `jpeg`, or `png`
- the Cloudinary account allows uploads to the configured folders

### Contact form fails

Check that:

- `MAILER_ADMIN_NAME`, `MAILER_ADMIN_EMAIL`, and `MAILER_API_KEY` are set
- the MailerSend sender is configured and allowed to send

## Security

Please report security vulnerabilities privately using the process in [SECURITY.md](SECURITY.md).

## License

This project is licensed under the terms included in [LICENSE](LICENSE).
