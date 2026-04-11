from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from accounts.views import health_check

urlpatterns = [
    path("admin/", admin.site.urls),
    path("health/", health_check, name="health"),

    # All app routes (accounts app handles everything)
    path("", include("accounts.urls")),

    # Password reset — Django built-in views
    path("password-reset/", include("django.contrib.auth.urls")),
]

# Serve uploaded media files during development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
