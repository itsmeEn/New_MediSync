from .settings import *  # noqa

# Use SQLite for isolated test runs to avoid clobbering dev/prod DB
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': ':memory:',
    }
}

# Speed up tests: disable password validators, channels layers, etc. as needed
AUTH_PASSWORD_VALIDATORS = []