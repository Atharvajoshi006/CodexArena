from django.urls import path
from . import views

urlpatterns = [

    # ── AUTH ──────────────────────────────────────────────────────────────────
    path("login/",   views.login_view,   name="login"),
    path("signup/",  views.signup_view,  name="signup"),
    path("logout/",  views.logout_view,  name="logout"),

    # ── PAGES ─────────────────────────────────────────────────────────────────
    path("",                        views.index_view,      name="index"),
    path("hackathons/",             views.hackathons_view, name="hackathons"),
    path("blogs/",                  views.blogs_view,      name="blogs"),
    path("profile/",                views.profile_view,    name="profile"),
    path("profile/<str:username>/", views.profile_view,    name="profile_user"),

    # ── API — BLOGS ───────────────────────────────────────────────────────────
    path("api/blogs/create/",         views.api_blog_create, name="api_blog_create"),
    path("api/blogs/<int:post_id>/like/", views.api_blog_like, name="api_blog_like"),

    # ── API — HACKATHONS ──────────────────────────────────────────────────────
    path("api/hackathons/create/",               views.api_hackathon_create, name="api_hackathon_create"),
    path("api/hackathons/<int:hackathon_id>/like/", views.api_hackathon_like, name="api_hackathon_like"),

    # ── API — USERS ───────────────────────────────────────────────────────────
    path("api/users/<int:user_id>/follow/", views.api_user_follow,    name="api_user_follow"),
    path("api/profile/update/",             views.api_profile_update, name="api_profile_update"),
]