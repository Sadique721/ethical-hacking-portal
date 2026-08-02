# Contributing to the Ethical Hacking Portal

We welcome contributions from security engineers, developers, and writers! Follow these guidelines to get started.

## Local Environment Setup

1. **Fork and Clone the Repository**
2. **Create a Virtual Environment**
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   ```
3. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```
4. **Copy the Environment Configuration**
   ```bash
   cp .env.example .env
   ```
5. **Run Database Migrations**
   ```bash
   python manage.py migrate
   ```
6. **Start the Development Server**
   ```bash
   python manage.py runserver
   ```

## Running Tests

We write unit and integration tests using `pytest`. Before pushing any changes, verify that the test suite passes successfully.

```bash
pytest --cov=. --cov-report=term-missing
```

## Adding CTF Challenges

To add new CTF challenges:
1. Log in to the Django Admin portal (`/admin/`).
2. Navigate to **CTF** -> **Challenges**.
3. Generate a SHA-256 hash of your flag (e.g. using `echo -n "FLAG{my_flag}" | shasum -a 256` or equivalent).
4. Save the challenge with its category, description, and the flag hash.
