
# Accounting App Backend

A backend application for an Accounting App built with Python and Django, containerized using Docker.

## Prerequisites

Ensure the following are installed on your computer:
- Python 3
- Docker
- Docker Compose
- Port 8000 is not in use

## Getting Started

Follow these steps to set up and run the application:

### Step 1: Create `config.json`
In the root directory, create a file named `config.json` with the following content:

```json
{
  "base_url": "your-site-url-here, e.g., http://localhost:8000/",
  "secret_key": "your-django-secret-key",
  "github": {
    "default_password": "your-default-password"
  },
  "google": {
    "default_password": "your-default-password"
  },
  "email": {
    "backend": "django.core.mail.backends.smtp.EmailBackend",
    "host": "smtp.gmail.com",
    "port": 587,
    "use_tls": true,
    "user": "your-email-address",
    "password": "your-email-password"
  }
}
```

Replace placeholders (`your-site-url-here`, `your-django-secret-key`, etc.) with the actual values.

---

### Step 2: Modify `config/nginx`
Update the `config/nginx` file with the following configuration:

```conf
upstream app {
  ip_hash;
  server app:8000;
}

server {
  listen 8000;
  server_name your-site-url-here;

  location /static/ {
    autoindex on;
    alias /code/collected_static/;
  }

  location / {
    proxy_pass http://app/;
  }
}
```

Replace `your-site-url-here` with your actual site URL.

---

### Step 3: Install `docker-compose`
Install Docker Compose using the following command:

```bash
pip install docker-compose
```

---

### Step 4: Build the Docker Images
Build the Docker images by running:

```bash
docker compose build
```

---

### Step 5: Start the Application
Start the application by running:

```bash
docker compose up
```

---

### Step 6: Expose the Application
Expose the application to the internet using a static IP address or a Cloudflare Tunnel.

---

## Project Structure

The project is structured as follows:

```bash
Backend
├── README.md              # Documentation for the backend
├── accounting_app         # Core accounting application
│   ├── __init__.py        # Module initialization
│   ├── admin.py           # Admin configuration
│   ├── apps.py            # App configuration
│   ├── models.py          # Database models
│   ├── serializers.py     # Data serialization (optional)
│   ├── templates          # HTML templates
│   │   ├── password_reset_form.html
│   │   └── password_reset_successful.html
│   ├── tests.py           # Unit tests
│   ├── urls.py            # URL routing
│   └── views.py           # View logic
├── accounting_system      # Project configuration
│   ├── __init__.py
│   ├── asgi.py            # ASGI entry point
│   ├── settings.py        # Django settings
│   ├── urls.py            # Global URL routing
│   └── wsgi.py            # WSGI entry point
├── api_reference.py       # API references (optional)
├── config.json            # Application configuration file
└── manage.py              # Django management script
```

---

## Notes

- The application is configured to run on port 8000 by default.
- For any issues or contributions, feel free to create an issue or submit a pull request on the project repository.

---
