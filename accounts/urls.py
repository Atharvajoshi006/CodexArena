from django.urls import path
from . import views

urlpatterns = [

    # ── AUTH ──────────────────────────────────────────────────────────────────
    path("login/",   views.login_view,   name="login"),
    path("signup/",  views.signup_view,  name="signup"),
    path("logout/",  views.logout_view,  name="logout"),
    
    # ── GOOGLE OAUTH ──────────────────────────────────────────────────────────
    path("google/login/",      views.google_login,      name="google_login"),
    path("google/callback/",   views.google_callback,   name="google_callback"),

    # ── PAGES ─────────────────────────────────────────────────────────────────
    path("",                        views.index_view,      name="index"),
    path("hackathons/",             views.hackathons_view, name="hackathons"),
    path("blogs/",                  views.blogs_view,      name="blogs"),
    path("profile/",                views.profile_view,    name="profile"),
    path("profile/<str:username>/", views.profile_view,    name="profile_user"),
    path("teams/",                  views.team_recruit_view, name="teams"),
    path("teams/<int:team_id>/",    views.team_detail_view, name="team_detail"),

    # ── API — BLOGS ───────────────────────────────────────────────────────────
    path("api/blogs/create/", views.api_blog_create, name="api_blog_create"),
    path("api/blogs/<int:post_id>/like/", views.api_blog_like, name="api_blog_like"),
    path(
        "api/blogs/<int:post_id>/comments/create/",
        views.api_blog_comment_create,
        name="api_blog_comment_create",
    ),

    # ── API — HACKATHONS ──────────────────────────────────────────────────────
    path("api/hackathons/create/",               views.api_hackathon_create, name="api_hackathon_create"),
    path("api/hackathons/<int:hackathon_id>/like/", views.api_hackathon_like, name="api_hackathon_like"),

    # ── API — USERS ───────────────────────────────────────────────────────────
    path("api/users/<int:user_id>/follow/", views.api_user_follow,    name="api_user_follow"),
    path("api/profile/update/",             views.api_profile_update, name="api_profile_update"),

    # ── API — TEAMS ───────────────────────────────────────────────────────────
    path("api/teams/create/",                           views.api_team_create,          name="api_team_create"),
    path("api/teams/<int:team_id>/invite/",             views.api_team_invite,          name="api_team_invite"),
    path("api/teams/<int:team_id>/remove-member/",      views.api_team_remove_member,   name="api_team_remove_member"),
    path("api/teams/<int:team_id>/update-status/",      views.api_team_update_status,   name="api_team_update_status"),
    path("api/teams/invites/<int:invite_id>/respond/",  views.api_team_invite_respond,  name="api_team_invite_respond"),
]
