import os
from .dev import *

SECRET_KEY = os.environ.get("SBLOG_SECRET_KEY", None)
DEBUG = False
ALLOWED_HOSTS = [".raesener.de", ".räsener.de"]

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": "sblog",
        "USER": "postgres",
        "PASSWORD": os.environ.get("POSTGRES_PASSWORD", None),
        "HOST": "db_sblog",
        "PORT": "5432",
    }
}

MEDIA_ROOT = os.path.abspath(os.path.join(BASE_DIR, "..", "sblog-media-files"))
