# Accounting App Backend

A backend application for an Accounting App built with Python.

## Prerequisites

Ensure the following are installed on your computer:
- Python 3
- Docker
- Docker Compose
- Port 8000 is not in use

## Getting Started

Follow these steps to set up and run the application:

1. Install `docker-compose`:

 ```bash
 pip install docker-compose
 ```

2. Build the Docker images:

 ```bash
 docker compose build
 ```

3. Start the application:

 ```bash
 docker compose up
 ```

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

## Notes

- The application is configured to run on port 8000 by default.
- For any issues or contributions, feel free to create an issue or a pull request.