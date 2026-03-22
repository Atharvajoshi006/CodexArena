from pathlib import Path

# ─── PATHS ───────────────────────────────────────────────────────────────────
BASE_DIR = Path(__file__).resolve().parent.parent


# ─── SECURITY ────────────────────────────────────────────────────────────────
# IMPORTANT: Change this to a long random string before deploying to production.
# Generate one with: python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
SECRET_KEY = "django-insecure-change-this-before-production-use-a-long-random-string"

# Set to False in production and add your domain to ALLOWED_HOSTS
DEBUG = True

ALLOWED_HOSTS = [
    "localhost",
    "127.0.0.1",
    # Add your production domain here, e.g. "codexarena.example.com"
]


# ─── APPLICATIONS ────────────────────────────────────────────────────────────
INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",

    # Your app
    "accounts.apps.AccountsConfig",
]


# ─── MIDDLEWARE ──────────────────────────────────────────────────────────────
MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]


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
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME":   BASE_DIR / "db.sqlite3",
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
LOGIN_URL          = "/login/"
LOGIN_REDIRECT_URL = "/"
LOGOUT_REDIRECT_URL = "/login/"


# ─── INTERNATIONALISATION ────────────────────────────────────────────────────
LANGUAGE_CODE = "en-us"
TIME_ZONE     = "Asia/Kolkata"
USE_I18N      = True
USE_TZ        = True


# ─── STATIC FILES ────────────────────────────────────────────────────────────
STATIC_URL  = "/static/"
STATIC_ROOT = BASE_DIR / "staticfiles"   # used by `collectstatic` for production

# Add a static folder at project root for your own CSS/JS if needed
STATICFILES_DIRS = [
    BASE_DIR / "static",
]


# ─── MEDIA FILES (user uploads — avatars, banners) ───────────────────────────
MEDIA_URL  = "/media/"
MEDIA_ROOT = BASE_DIR / "media"


# ─── DEFAULT PK ──────────────────────────────────────────────────────────────
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"


# ─── MESSAGES ────────────────────────────────────────────────────────────────
from django.contrib.messages import constants as message_constants
MESSAGE_TAGS = {
    message_constants.ERROR: "error",
    message_constants.SUCCESS: "success",
}


# ─── SESSION ─────────────────────────────────────────────────────────────────
SESSION_COOKIE_AGE     = 60 * 60 * 24 * 14   # 14 days
SESSION_COOKIE_SECURE  = not DEBUG            # True in production (HTTPS only)
CSRF_COOKIE_SECURE     = not DEBUG


# ─── SECURITY HEADERS (production) ───────────────────────────────────────────
# Uncomment these when DEBUG = False
# SECURE_HSTS_SECONDS        = 31536000
# SECURE_HSTS_INCLUDE_SUBDOMAINS = True
# SECURE_SSL_REDIRECT        = True
# X_FRAME_OPTIONS            = "DENY"