# django-ackee-middleware

[![CI](https://github.com/suda/django-ackee-middleware/workflows/CI/badge.svg)](https://github.com/suda/django-ackee-middleware/actions)
[![codecov](https://codecov.io/gh/suda/django-ackee-middleware/branch/master/graph/badge.svg)](https://codecov.io/gh/suda/django-ackee-middleware)
[![License](https://img.shields.io/pypi/l/django-ackee-middleware)](LICENSE)
[![PyPI](https://img.shields.io/pypi/v/django-ackee-middleware)](https://pypi.org/project/django-ackee-middleware/)

> [Django](https://www.djangoproject.com/) middleware reporting requests to [Ackee](https://ackee.electerious.com/), self-hosted  analytics tool for those who care about privacy. Alternative to using the client-side JS tracker.

## Installation

```
$ pip install django-ackee-middleware
```

If you don't have the Ackee instance yet, you can quickly [deploy it on Heroku](https://docs.ackee.electerious.com/#/docs/Get%20started#with-heroku).

## Configuration

Add the middleware as the first one in your Django `settings.py`:

```python
MIDDLEWARE = [
    "ackee.middleware.TrackerMiddleware",
    "django.middleware.security.SecurityMiddleware",
    ...
]
```

Then add the following properties:

```python
ACKEE_SERVER = "https://myackeeserver.com"
ACKEE_DOMAIN_ID = "YOUR DOMAIN ID"
ACKEE_IGNORED_PATHS = [
    "^/admin/.*"
]
```

Remember to change the server and domain ID to your values.