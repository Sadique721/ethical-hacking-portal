# 🔒 Ethical Hacking Portal

[![Django](https://img.shields.io/badge/Django-5.1%20%7C%206.0-092E20?style=for-the-badge&logo=django&logoColor=white)](https://www.djangoproject.com/)
[![Bootstrap](https://img.shields.io/badge/Bootstrap-5.0.2-563D7C?style=for-the-badge&logo=bootstrap&logoColor=white)](https://getbootstrap.com/)
[![SQLite](https://img.shields.io/badge/SQLite-3.0-07405E?style=for-the-badge&logo=sqlite&logoColor=white)](https://www.sqlite.org/)
[![WhiteNoise](https://img.shields.io/badge/Static_Serving-WhiteNoise-blue?style=for-the-badge)](https://whitenoise.readthedocs.io/)

A secure, educational web portal designed for cybersecurity training, penetration testing resources, and interactive student collaboration. Built with Django and styled with a clean Bootstrap 5 interface, utilizing local static CSS and JS.

---

## 🌟 Key Features

*   **Secure Authentication**: Role-based signup, sign-in, and log-out flows with Django's built-in session framework.
*   **Password Reset Pipeline**: Multi-step password recovery workflow (request email, verification links, confirm, complete).
*   **Extended User Profiles**: Automated profile creation for new users via Django database signals, supporting user bios, locations, and profile picture uploads.
*   **Local Assets**: Bootstrap CSS and JS are served entirely locally (`static/css/` and `static/js/`), ensuring offline responsiveness and removing reliance on external CDNs.
*   **Static Resource Management**: Production-ready static configuration utilizing **WhiteNoise** for automatic file compression and client caching.
*   **Database Migrations**: Integrated database model migrations ready for SQLite or PostgreSQL.

---

## 📁 Repository Layout

The project files are structured as a standard Django application:

```text
ethical-hacking-portal/
├── manage.py               # Django Command Line Utility
├── requirements.txt        # Python package dependencies
├── .gitignore              # Ignored files (virtual envs, db files)
├── note.txt                # In-depth architectural workflow documentation
├── README.md               # Quick-start and Render.com deployment guide
│
├── myfirstpro/             # Django Project Configuration Directory
│   ├── settings.py         # Configs (apps, middleware, static/media, database)
│   ├── urls.py             # Root URL routing configurations
│   ├── wsgi.py / asgi.py   # Web server integrations
│   └── __init__.py
│
├── MSA/                    # Django Application Directory (Main Hacking Portal)
│   ├── migrations/         # Database migrations directory
│   ├── admin.py            # Model configurations in Django Admin
│   ├── forms.py            # Forms for registration and profile edit validation
│   ├── models.py           # Database schemas for Profiles and Contacts
│   ├── urls.py             # App-specific view routing
│   ├── views.py            # View functions and business logic
│   └── __init__.py
│
├── templates/              # HTML layout elements
│   ├── base.html           # Main template containing navbar, footer, messages and scripts
│   ├── index.html          # Interactive landing page with information carousels
│   ├── about.html          # Operations information and operator bios
│   ├── services.html       # Overview of security audit offerings
│   ├── contact.html        # Admin alert submission form
│   ├── dashboard.html      # Logged-in training console
│   ├── profile.html        # Public operator bio details
│   ├── edit_profile.html   # Profile settings page
│   ├── login.html          # User authentication portal login
│   ├── register.html       # User authentication portal sign-up
│   └── registration/       # Django Password Reset flow template folder
│
└── static/                 # Static directories
    ├── css/
    │   └── bootstrap.min.css      # Local Bootstrap stylesheet
    └── js/
        └── bootstrap.bundle.min.js # Local Bootstrap bundle scripts
```

---

## 🚀 How to Run Locally

### 1. Setup Environment
Ensure Python 3 is installed. Clone the repository, navigate into the project, and install the dependencies listed in `requirements.txt`:

```bash
pip install -r requirements.txt
```

### 2. Apply Database Migrations
Create and configure your database models:

```bash
python manage.py makemigrations MSA
python manage.py migrate
```

### 3. Launch Development Server
Start the local server:

```bash
python manage.py runserver
```

Now open your browser and navigate to **[http://127.0.0.1:8000/](http://127.0.0.1:8000/)** to access the portal.

---

## ☁️ Deploying on Render.com

This project can be deployed easily on **[Render.com](https://render.com/)**:

### Step 1: Create a Render Web Service
1. Log in to Render and click **New +** -> **Web Service**.
2. Connect your GitHub repository containing this project.

### Step 2: Configure Environment and Commands
Configure your web service with these specifications:
*   **Runtime**: `Python`
*   **Build Command**:
    ```bash
    python -m pip install -r requirements.txt && python manage.py collectstatic --noinput && python manage.py migrate
    ```
*   **Start Command**:
    ```bash
    gunicorn myfirstpro.wsgi:application --bind 0.0.0.0:$PORT
    ```

### Step 3: Add Environment Variables (Settings Panel)
Add the following key-value pairs in the **Environment** section:
*   `DEBUG`: `False` (for production safety)
*   `SECRET_KEY`: *[A long, random secret sequence]*
*   `ALLOWED_HOSTS`: `your-app-subdomain.onrender.com`

Render will compile the static assets automatically during build and serve them safely via `WhiteNoise`, making your application fully functional and live!
