import os
from pathlib import Path
from urllib.parse import urlparse

from django.contrib.messages import constants as message_constants

try:
    import dj_database_url
except ImportError:  # pragma: no cover - available after installing requirements.txt
    dj_database_url = None

try:
    import whitenoise  # noqa: F401
except ImportError:  # pragma: no cover - available after installing requirements.txt
    HAS_WHITENOISE = False
else:
    HAS_WHITENOISE = True

# ─── PATHS ───────────────────────────────────────────────────────────────────
BASE_DIR = Path(__file__).resolve().parent.parent


def env_bool(name, default=False):
    value = os.getenv(name)
    if value is None:
        return default
    return value.strip().lower() in {"1", "true", "yes", "on"}


def env_list(name, default=None):
    value = os.getenv(name)
    if value is None:
        return list(default or [])
    return [item.strip() for item in value.split(",") if item.strip()]


def add_host_from_url(hosts, url_value):
    if not url_value:
        return
    parsed = urlparse(url_value)
    candidate = parsed.netloc or parsed.path
    candidate = candidate.split("@")[-1].split(":")[0].strip().lower()
    if candidate and candidate not in hosts:
        hosts.append(candidate)


# ─── SECURITY ────────────────────────────────────────────────────────────────
SECRET_KEY = os.getenv(
    "SECRET_KEY",
    "django-insecure-change-this-before-production-use-a-long-random-string",
)
DEBUG = env_bool("DEBUG", True)

ALLOWED_HOSTS = env_list("ALLOWED_HOSTS", ["127.0.0.1", "localhost"])
for host in filter(None, [os.getenv("RENDER_EXTERNAL_HOSTNAME"), os.getenv("VERCEL_URL")]):
    if host not in ALLOWED_HOSTS:
        ALLOWED_HOSTS.append(host)
for public_url in [os.getenv("BACKEND_PUBLIC_URL"), os.getenv("FRONTEND_URL")]:
    add_host_from_url(ALLOWED_HOSTS, public_url)

CSRF_TRUSTED_ORIGINS = env_list(
    "CSRF_TRUSTED_ORIGINS",
    ["http://127.0.0.1:8000", "http://localhost:8000"],
)
for public_url in [os.getenv("BACKEND_PUBLIC_URL"), os.getenv("FRONTEND_URL")]:
    if public_url and public_url not in CSRF_TRUSTED_ORIGINS:
        CSRF_TRUSTED_ORIGINS.append(public_url)


# ─── APPLICATIONS ────────────────────────────────────────────────────────────
INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
]

if HAS_WHITENOISE:
    INSTALLED_APPS.append("whitenoise.runserver_nostatic")

INSTALLED_APPS.extend(
    [
        "django.contrib.staticfiles",
        "accounts.apps.AccountsConfig",
    ]
)


# ─── MIDDLEWARE ──────────────────────────────────────────────────────────────
MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
]

if HAS_WHITENOISE:
    MIDDLEWARE.append("whitenoise.middleware.WhiteNoiseMiddleware")

MIDDLEWARE.extend(
    [
        "django.contrib.sessions.middleware.SessionMiddleware",
        "django.middleware.common.CommonMiddleware",
        "django.middleware.csrf.CsrfViewMiddleware",
        "django.contrib.auth.middleware.AuthenticationMiddleware",
        "django.contrib.messages.middleware.MessageMiddleware",
        "django.middleware.clickjacking.XFrameOptionsMiddleware",
    ]
)


# ─── URLS & WSGI ─────────────────────────────────────────────────────────────
ROOT_URLCONF = "codexarena.urls"
WSGI_APPLICATION = "codexarena.wsgi.application"


# ─── TEMPLATES ───────────────────────────────────────────────────────────────
TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        # Django will look for templates in this folder at the project root
        "DIRS": [BASE_DIR / "templates"],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]


# ─── DATABASE ────────────────────────────────────────────────────────────────
# SQLite is fine for development. Switch to PostgreSQL for production.
if os.getenv("DATABASE_URL"):
    if dj_database_url is None:
        raise RuntimeError("Install dj-database-url before using DATABASE_URL.")
    DATABASES = {
        "default": dj_database_url.parse(
            os.environ["DATABASE_URL"],
            conn_max_age=600,
            conn_health_checks=True,
        )
    }
else:
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.sqlite3",
            "NAME": BASE_DIR / "db.sqlite3",
        }
    }

# ── Production PostgreSQL (uncomment & fill in when deploying) ────────────────
# DATABASES = {
#     "default": {
#         "ENGINE":   "django.db.backends.postgresql",
#         "NAME":     "codexarena_db",
#         "USER":     "your_db_user",
#         "PASSWORD": "your_db_password",
#         "HOST":     "localhost",
#         "PORT":     "5432",
#     }
# }


# ─── AUTH ────────────────────────────────────────────────────────────────────
AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

# Where Django redirects after login/logout
LOGIN_URL = "/login/"
LOGIN_REDIRECT_URL = "/"
LOGOUT_REDIRECT_URL = "/login/"


# ─── INTERNATIONALISATION ────────────────────────────────────────────────────
LANGUAGE_CODE = "en-us"
TIME_ZONE = "Asia/Kolkata"
USE_I18N = True
USE_TZ = True


# ─── STATIC FILES ────────────────────────────────────────────────────────────
STATIC_URL = "/static/"
STATIC_ROOT = BASE_DIR / "staticfiles"
STATIC_SOURCE_DIR = BASE_DIR / "static"
STATICFILES_DIRS = [STATIC_SOURCE_DIR] if STATIC_SOURCE_DIR.exists() else []
STORAGES = {
    "default": {
        "BACKEND": "django.core.files.storage.FileSystemStorage",
    },
    "staticfiles": {
        "BACKEND": (
            "whitenoise.storage.CompressedManifestStaticFilesStorage"
            if HAS_WHITENOISE
            else "django.contrib.staticfiles.storage.StaticFilesStorage"
        ),
    },
}


# ─── MEDIA FILES (user uploads — avatars, banners) ───────────────────────────
MEDIA_URL = "/media/"
MEDIA_ROOT = BASE_DIR / "media"


# ─── DEFAULT PK ──────────────────────────────────────────────────────────────
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"


# ─── MESSAGES ────────────────────────────────────────────────────────────────
MESSAGE_TAGS = {
    message_constants.ERROR: "error",
    message_constants.SUCCESS: "success",
}


# ─── SESSION ─────────────────────────────────────────────────────────────────
SESSION_COOKIE_AGE = 60 * 60 * 24 * 14
SESSION_COOKIE_SECURE = not DEBUG
CSRF_COOKIE_SECURE = not DEBUG
SESSION_COOKIE_SAMESITE = os.getenv("SESSION_COOKIE_SAMESITE", "Lax")
CSRF_COOKIE_SAMESITE = os.getenv("CSRF_COOKIE_SAMESITE", "Lax")
SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
USE_X_FORWARDED_HOST = True


# ─── SECURITY HEADERS (production) ───────────────────────────────────────────
if not DEBUG:
    SECURE_HSTS_SECONDS = int(os.getenv("SECURE_HSTS_SECONDS", "31536000"))
    SECURE_HSTS_INCLUDE_SUBDOMAINS = env_bool("SECURE_HSTS_INCLUDE_SUBDOMAINS", True)
    SECURE_HSTS_PRELOAD = env_bool("SECURE_HSTS_PRELOAD", True)
    SECURE_SSL_REDIRECT = env_bool("SECURE_SSL_REDIRECT", True)
    SECURE_REFERRER_POLICY = "strict-origin-when-cross-origin"
    X_FRAME_OPTIONS = "DENY"


# ─── GOOGLE OAUTH ───────────────────────────────────────────────────────────
GOOGLE_OAUTH_CLIENT_ID = os.getenv("GOOGLE_OAUTH_CLIENT_ID", "")
GOOGLE_OAUTH_CLIENT_SECRET = os.getenv("GOOGLE_OAUTH_CLIENT_SECRET", "")
GOOGLE_OAUTH_REDIRECT_URI = os.getenv(
    "GOOGLE_OAUTH_REDIRECT_URI",
    "http://localhost:8000/accounts/google/callback/"
)
