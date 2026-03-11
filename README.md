# 🚀 Flask Portfolio & Micro-CMS

A bespoke, high-performance portfolio and content management system built with **Python** and **Flask**. This project evolved from a 100-day coding challenge into a fully functional "In-Place" CMS, allowing for dynamic content updates without the need for a traditional, detached administrative backend.



## 🛠️ Tech Stack

* **Backend:** Python 3.12, Flask
* **WSGI Server:** **Gunicorn** (Production)
* **Database:** **PostgreSQL** (Production via **Psycopg**), SQLite (Development)
* **ORM:** SQLAlchemy (2.0 Syntax)
* **Frontend:** Bootstrap 5, Jinja2, CSS3 (Glassmorphism/Bento UI aesthetic)
* **Deployment:** Render (CI/CD via GitHub)
* **Rich Text:** Quill.js Integration

## ✨ Key Features

* **Dynamic Micro-CMS:** Seamlessly add, edit, and delete projects and blog posts directly through the UI.
* **In-Place Administration:** Administrative controls (edit/delete buttons) appear contextually only when logged in as the admin user.
* **Bento-Grid Design:** A modern, scannable layout optimized for showcasing engineering projects and technical writing.
* **Automated Deployment:** Fully integrated CI/CD pipeline—push to GitHub, and Render handles the build and deployment.
* **Secure Authentication:** Flask-Login managed sessions with salted password hashing via Werkzeug.
* **Contact Integration:** Fully functional contact page powered by the **Mailer API**. Setup an account at **mailersend.com**.

## 📥 Installation & Setup

### 1. Clone the repository
```bash
git clone [https://github.com/yourusername/portfolio-website.git](https://github.com/yourusername/portfolio-website.git)
cd portfolio-website
```

### 2. Environmentals
Environment-specific config and secrets (such as API keys). 
```
FLASK_SECRET_KEY="your_secret_key"
DATABASE_URL="sqlite:///portfolio.db"
MAILER_API_KEY="your Access Token from mailersend.com"
MAILER_ADMIN_NAME="your sender name"
MAILER_ADMIN_EMAIL="your email address"
```

### 3. Build Command
Runs this command to build your app before each deploy
```
pip install -r requirements.txt
```

### 3. Start Command
Run this command to start your app with each deploy
```
gunicorn main:app
```


## 🚀 Deployment & Initial Setup
This project is optimized for deployment on Render. Ensure your DATABASE_URL is mapped to your PostgreSQL instance and MAILER_API_KEY is configured in the Render environment settings.

### The Setup Page
Upon the first deployment, the application detects an empty database and automatically redirects to the Initial Setup Page. This one-time process prompts you for:

* **Admin Name:** Your professional name for the site headers.

* **Credentials:** Your email and a secure password for admin access.

* **Bio/Profile:** Initial "About Me" content to populate your profile.


### You Admin Access

To manage your content, navigate to the **/login** path. Once authenticated, the site reveals the administrative interface:

* **Admin Navigation:** Links to create new posts or projects appear in the navbar.

* **Direct Editing:** **"Edit"** and **"Delete"** icons appear on all project and post cards.

* **Dynamic Tech Stack:** Update your skills and profile details on the fly.