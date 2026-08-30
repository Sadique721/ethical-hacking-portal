<!-- ========== NEW: ANIMATED WAVE HEADER ========== -->
<p align="center">
  <img src="https://capsule-render.vercel.app/api?type=waving&color=0:22d3ee,100:8b5cf6&height=200&section=header&text=ethical-hacking-portal&fontSize=50&fontColor=ffffff&animation=fadeIn&fontAlignY=38&desc=Ethical%20Hacking%20%26%20Cybersecurity%20Portal&descAlignY=60&descAlign=50" width="100%">
</p>

<!-- ========== NEW: TYPING ANIMATION INTRO ========== -->
<p align="center">
  <img src="https://readme-typing-svg.demolab.com?font=Fira+Code&weight=600&size=24&duration=3000&pause=500&color=22D3EE&center=true&vCenter=true&width=700&lines=Cybersecurity Portal;Ethical Hacking Tutorials;Django Web Security;Interactive Learning Platform" alt="Typing SVG">
</p>

<!-- ========== NEW: AUTHOR & ARCHITECT SECTION ========== -->
## 👨‍💻 Author & Architect

<table>
<tr>
<td align="center" width="160">
  <a href="https://github.com/Sadique721">
    <img src="https://avatars.githubusercontent.com/Sadique721" width="110" style="border-radius:50%"><br>
    <b>Md Sadique Amin</b><br>
    <sub>Backend Java Developer</sub>
  </a>
</td>
<td>

**Md Sadique Amin** — Backend Java Developer.

- 🔗 GitHub: [@Sadique721](https://github.com/Sadique721)
- 📧 Email: mdsadiqueamin721786@gmail.com
- 🏗️ Built: Enterprise BSS-OSS Telecom Suite, Backend Java Developer, IR Interconnect & Roaming

</td>
</tr>
</table>

<!-- ========== NEW: SYSTEM DIAGRAM SECTION ========== -->
## 📊 System Architecture & Workflow

```mermaid
flowchart TD
    A[Hacker / Pentester Sandbox] --> B[Django Web portal]
    B --> C{Security Labs}
    C --> D[SQL Injection Lab]
    C --> E[XSS vulnerability Sandbox]
    C --> F[Secure Coding Reference]
    D --> G[DB Attack Simulation]
    E --> H[Script Injection Simulation]
```

---

# 🔒 Security Training & Penetration Testing Portal

[![Django](https://img.shields.io/badge/Django-6.0.7-092E20?style=for-the-badge&logo=django&logoColor=white)](https://www.djangoproject.com/)
[![DRF](https://img.shields.io/badge/DRF-3.17.1-red?style=for-the-badge&logo=django&logoColor=white)](https://www.django-rest-framework.org/)
[![JWT](https://img.shields.io/badge/JWT-SimpleJWT-darkblue?style=for-the-badge&logo=json-web-tokens)](https://django-rest-framework-simplejwt.readthedocs.io/)
[![Bootstrap](https://img.shields.io/badge/Bootstrap-5.3-563D7C?style=for-the-badge&logo=bootstrap&logoColor=white)](https://getbootstrap.com/)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-16.0-4169E1?style=for-the-badge&logo=postgresql&logoColor=white)](https://www.postgresql.org/)
[![Docker](https://img.shields.io/badge/Docker-Containerized-blue?style=for-the-badge&logo=docker&logoColor=white)](https://www.docker.com/)
[![pytest](https://img.shields.io/badge/pytest-Passing-brightgreen?style=for-the-badge&logo=pytest)](https://docs.pytest.org/)

An advanced, production-grade cybersecurity training platform designed for security researchers to solve CTF challenges, analyze security headers, search CVEs, and generate PDF pentest reports. Built using Django 6.0, Django REST Framework, custom TOTP 2FA security, HTMX, and containerized with Docker.

---

## 🌟 Key Features

*   **🏆 Capture The Flag (CTF) Module:** Gamified training module. Flags are validated using secure SHA-256 hashing. Submission rate-limiting via `django-ratelimit` prevents brute-forcing, and the leaderboard updates in real-time using HTMX.
*   **🛡️ Secure Custom 2FA (TOTP):** Two-factor authentication implemented in pure Python/Django using `pyotp` and base64 QR code rendering. Integrates seamlessly with Google Authenticator or Authy.
*   **🔎 Async CVE Lookup Tool:** Real-time lookup querying the National Vulnerability Database (NVD) REST API using Django 6.0's async views and `httpx`. Responses are cached locally via Django's caching framework.
*   **🔗 HTTP Security Header Analyzer:** Audits response headers (CSP, HSTS, X-Frame-Options) for public URLs, scoring configurations (A+ to F) and providing remediation insights.
*   **📄 PDF Report Generator:** Compiles pentest findings into a professional, dark-themed PDF report using ReportLab. Tasks are managed asynchronously via Django 6.0's new native background tasks framework (`django.tasks`).
*   **🧑💻 Profile & Image Pipeline:** Profile details with skill levels, specializations, social profiles, and points. Profile picture uploads are checked (max 2MB, formats), EXIF metadata is stripped to protect user privacy (prevents GPS leaks), and converted to `.webp` format.
*   **🔐 Hardened Security Controls:** Enforces native Django 6.0 Content Security Policy (CSP) headers, authentication lockouts (`django-axes`) for brute-force login shielding, and sanitized write-ups (using `bleach`) to block stored XSS.
*   **📊 REST API & Interactive Docs:** Exposes `/api/v1/` endpoints for profiles, challenges, and tools with JWT auth and auto-generated Swagger UI via `drf-spectacular` at `/api/docs/`.
*   **🐳 Containerized Environment:** Complete Docker + docker-compose orchestration bundling Django, PostgreSQL, and Redis cache.

---

## 📁 Repository Structure

```text
ethical-hacking-portal/
├── config/                 # Project Configuration (Renamed from myfirstpro)
│   ├── settings/           # 12-Factor Settings (base.py, dev.py, prod.py)
│   ├── urls.py             # Root URL Routing
│   ├── wsgi.py / asgi.py   # WSGI/ASGI Gateways
│   └── __init__.py
├── MSA/                    # Main Application Directory (Profiles, Auth)
│   ├── forms.py            # User Details & File Validators
│   ├── models.py           # User Profile & Contact schemas
│   ├── views.py            # Logical views & Auth controller
│   ├── views_2fa.py        # Custom 2FA registration & validation views
│   └── tests.py            # Unit tests (initals SVG, file validators)
├── ctf/                    # Capture The Flag Application
│   ├── models.py           # Challenge & Submission (SHA-256 checks, scoring)
│   ├── views.py            # Flag submission, rate limits, leaderboard
│   └── tests.py            # Pytest tests (flag verification, scoring signals, DRF API)
├── utilities/              # Cybersecurity tools
│   ├── tasks.py            # PDF report background task (ReportLab)
│   └── views.py            # Async CVE lookup & Header analyzer views
├── writeups/               # Markdown Blog
│   └── views.py            # Sanitized Markdown rendering (XSS protection)
├── audit/                  # Security Audit trail
│   ├── signals.py          # Intercepts login, logouts, failures & IPs
│   └── models.py           # Immutable Audit entries
├── api/                    # Centralized REST API routing
│   ├── views.py            # DRF ViewSets & Swagger-documented endpoints
│   └── urls.py             # JWT endpoints & Swagger UI urls
├── templates/              # HTML layout elements (HTMX, Terminal Dark Theme)
├── Dockerfile              # App container definition
├── docker-compose.yml      # Multi-container orchestrator (Django, Postgres, Redis)
├── pytest.ini              # Pytest configurations
└── requirements.txt        # Pinned packages
```

---

## 🐳 Quick-start: Run with Docker Compose

Running the entire stack (Django, PostgreSQL, and Redis) is simplified into a single command:

1. **Clone the repo and navigate to directory:**
   ```bash
   git clone https://github.com/Sadique721/ethical-hacking-portal.git
   cd ethical-hacking-portal
   ```
2. **Start the containers:**
   ```bash
   docker-compose up --build
   ```
3. **Run database migrations inside the container:**
   ```bash
   docker-compose exec web python manage.py migrate
   ```
4. **Create a superuser to access the Admin Panel:**
   ```bash
   docker-compose exec web python manage.py createsuperuser
   ```
5. **Access the portal:**
   - Web application: http://localhost:8000
   - Swagger API Documentation: http://localhost:8000/api/v1/docs/
   - Django Admin (modern Jazzmin theme): http://localhost:8000/admin/

---

## 🚀 Running Locally (Without Docker)

1. **Install python packages:**
   ```bash
   pip install -r requirements.txt
   ```
2. **Create local environment file:**
   Copy `.env.example` to `.env` and configure credentials:
   ```bash
   cp .env.example .env
   ```
3. **Execute database migrations:**
   ```bash
   python manage.py migrate
   ```
4. **Launch development server:**
   ```bash
   python manage.py runserver
   ```

---

## 🧪 Testing and Quality Control

We run a suite of unit and integration tests checking profile pipelines, CTF signals, and REST endpoints.

Run the test suite with coverage reporting:
```bash
pytest
```


<!-- ========== NEW: FOOTER WAVE ANIMATION ========== -->
<p align="center">
  <img src="https://capsule-render.vercel.app/api?type=waving&color=0:22d3ee,100:8b5cf6&height=120&section=footer&width=100%">
</p>