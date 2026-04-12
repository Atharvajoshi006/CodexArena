import json
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST, require_http_methods
from django.http import JsonResponse
from django.db.models import Count, Prefetch
from django.conf import settings
import os
import requests
from urllib.parse import urlencode, quote_plus
import secrets

from .models import BlogPost, BlogComment, Hackathon, Team, TeamMember, TeamInvite


# ══════════════════════════════════════════════════════════════════════════════
#  HELPER
# ══════════════════════════════════════════════════════════════════════════════

def _json_body(request):
    """Parse JSON request body safely."""
    try:
        return json.loads(request.body)
    except (json.JSONDecodeError, ValueError):
        return {}


def health_check(request):
    """Simple health probe for hosting platforms."""
    return JsonResponse({"status": "ok"})


def _display_name(user):
    full_name = user.get_full_name().strip()
    return full_name or user.username


def _user_initials(user):
    display_name = _display_name(user)
    parts = display_name.split()
    if len(parts) >= 2:
        return f"{parts[0][0]}{parts[1][0]}".upper()
    return display_name[:2].upper()


def _user_gradient(user):
    profile = getattr(user, "profile", None)
    if profile and profile.avatar_gradient:
        return profile.avatar_gradient
    return "linear-gradient(135deg,#2f81f7,#58a6ff)"


# ══════════════════════════════════════════════════════════════════════════════
#  AUTH VIEWS
# ══════════════════════════════════════════════════════════════════════════════

def login_view(request):
    """GET → render login page | POST → authenticate & redirect."""
    if request.user.is_authenticated:
        return redirect("/")

    error = None
    if request.method == "POST":
        username = request.POST.get("username", "").strip()
        password = request.POST.get("password", "")

        if not username or not password:
            error = "Please fill in both fields."
        else:
            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)
                next_url = request.GET.get("next", "/")
                return redirect(next_url)
            else:
                error = "Invalid username or password."

    return render(request, "login.html", {"error": error})


def signup_view(request):
    """GET → render signup page | POST → create user & redirect."""
    if request.user.is_authenticated:
        return redirect("/")

    error = None
    if request.method == "POST":
        username  = request.POST.get("username", "").strip()
        email     = request.POST.get("email", "").strip()
        password1 = request.POST.get("password1", "")
        password2 = request.POST.get("password2", "")

        if not username or not email or not password1:
            error = "Please fill in all fields."
        elif password1 != password2:
            error = "Passwords do not match."
        elif len(password1) < 8:
            error = "Password must be at least 8 characters."
        elif User.objects.filter(username=username).exists():
            error = "That username is already taken."
        elif User.objects.filter(email=email).exists():
            error = "An account with that email already exists."
        else:
            user = User.objects.create_user(username=username, email=email, password=password1)
            login(request, user)
            return redirect("/")

    return render(request, "signup.html", {"error": error})


def logout_view(request):
    """POST → log out and redirect to login."""
    if request.method == "POST":
        logout(request)
    return redirect("/login/")


# ══════════════════════════════════════════════════════════════════════════════
#  GOOGLE OAUTH VIEWS
# ══════════════════════════════════════════════════════════════════════════════

def google_login(request):
    """Redirect user to Google OAuth consent screen."""
    client_id = settings.GOOGLE_OAUTH_CLIENT_ID
    redirect_uri = settings.GOOGLE_OAUTH_REDIRECT_URI

    if not client_id or not settings.GOOGLE_OAUTH_CLIENT_SECRET:
        return redirect("/login/?error=" + quote_plus("Google OAuth is not configured on this server."))

    # Store redirect URL in session
    next_url = request.GET.get("next", "/")
    request.session["oauth_next"] = next_url

    # Generate state token for CSRF protection
    state = secrets.token_urlsafe(32)
    request.session["oauth_state"] = state

    params = {
        "client_id": client_id,
        "redirect_uri": redirect_uri,
        "response_type": "code",
        "scope": "openid email profile",
        "state": state,
        "access_type": "online",
    }

    google_auth_url = "https://accounts.google.com/o/oauth2/v2/auth?" + urlencode(params)
    return redirect(google_auth_url)


def _make_unique_username(base):
    """
    Return *base* if available; otherwise append a short random suffix until unique.
    Keeps the result within Django's 150-char username limit.
    """
    base = base[:30]  # leave room for the suffix
    candidate = base
    while User.objects.filter(username=candidate).exists():
        suffix = secrets.token_hex(3)  # 6 hex chars
        candidate = f"{base[:23]}_{suffix}"  # max 30 chars
    return candidate


def google_callback(request):
    """Handle Google OAuth callback."""
    code = request.GET.get("code")
    state = request.GET.get("state")
    google_error = request.GET.get("error")

    # Error returned by Google (e.g. user cancelled)
    if google_error:
        return redirect("/login/?error=" + quote_plus(f"Google sign-in was cancelled or failed: {google_error}"))

    if not code or not state:
        return redirect("/login/?error=" + quote_plus("Missing authorization code or state."))

    # Verify state token to prevent CSRF
    session_state = request.session.get("oauth_state")
    if not session_state or session_state != state:
        return redirect("/login/?error=" + quote_plus("Invalid state token. Please try signing in again."))

    try:
        # ── 1. Exchange authorisation code for tokens ──────────────────────────
        token_response = requests.post(
            "https://oauth2.googleapis.com/token",
            data={
                "client_id": settings.GOOGLE_OAUTH_CLIENT_ID,
                "client_secret": settings.GOOGLE_OAUTH_CLIENT_SECRET,
                "code": code,
                "redirect_uri": settings.GOOGLE_OAUTH_REDIRECT_URI,
                "grant_type": "authorization_code",
            },
            timeout=10,
        )
        token_response.raise_for_status()
        tokens = token_response.json()

        access_token = tokens.get("access_token")
        if not access_token:
            token_error = tokens.get("error_description") or tokens.get("error") or "No access token returned"
            return redirect("/login/?error=" + quote_plus(f"Token exchange failed: {token_error}"))

        # ── 2. Fetch user info from Google ─────────────────────────────────────
        userinfo_response = requests.get(
            "https://openidconnect.googleapis.com/v1/userinfo",
            headers={"Authorization": f"Bearer {access_token}"},
            timeout=10,
        )
        userinfo_response.raise_for_status()
        userinfo = userinfo_response.json()

        email = userinfo.get("email", "").strip().lower()
        name = userinfo.get("name", "").strip()

        if not email:
            return redirect("/login/?error=" + quote_plus("Could not retrieve your email from Google."))

        # ── 3. Find or create local Django user ────────────────────────────────
        try:
            user = User.objects.get(email=email)
            # Update name on returning users
            if name:
                parts = name.split(maxsplit=1)
                user.first_name = parts[0][:30]
                user.last_name = parts[1][:30] if len(parts) > 1 else ""
                user.save(update_fields=["first_name", "last_name"])
        except User.DoesNotExist:
            # Derive a unique username from the email local-part
            base = email.split("@")[0]
            username = _make_unique_username(base)
            parts = name.split(maxsplit=1) if name else []
            user = User.objects.create_user(
                username=username,
                email=email,
                password=None,  # unusable password — OAuth only
                first_name=parts[0][:30] if parts else "",
                last_name=parts[1][:30] if len(parts) > 1 else "",
            )

        # ── 4. Log the user in ─────────────────────────────────────────────────
        login(request, user, backend="django.contrib.auth.backends.ModelBackend")

        # Clean up session state
        request.session.pop("oauth_state", None)
        next_url = request.session.pop("oauth_next", "/")
        return redirect(next_url)

    except requests.RequestException as exc:
        return redirect("/login/?error=" + quote_plus(f"Network error during sign-in: {str(exc)[:80]}"))
    except Exception as exc:
        return redirect("/login/?error=" + quote_plus(f"Unexpected error: {str(exc)[:80]}"))


# ══════════════════════════════════════════════════════════════════════════════
#  PAGE VIEWS
# ══════════════════════════════════════════════════════════════════════════════

def index_view(request):
    """Home page — featured hackathons + recent blogs."""
    featured_hackathons = Hackathon.objects.filter(
        is_featured=True, is_approved=True
    ).order_by("-created_at")[:3]

    recent_blogs = BlogPost.objects.select_related("author").order_by("-created_at")[:3]

    hackathon_count = Hackathon.objects.filter(is_approved=True).count()
    user_count      = User.objects.count()

    user_teams = []
    if request.user.is_authenticated:
        user_teams = list(request.user.teams_led.all()) + list(request.user.teams_in.all())

    ctx = {
        "featured_hackathons": featured_hackathons,
        "recent_blogs":        recent_blogs,
        "hackathon_count":     hackathon_count,
        "user_count":          user_count,
        "user_teams":          user_teams,
    }
    return render(request, "index.html", ctx)


def hackathons_view(request):
    """Hackathons listing page."""
    hackathons = Hackathon.objects.filter(is_approved=True).order_by("-is_featured", "-created_at")

    # Pass IDs the current user has liked (for button state)
    user_liked_ids = set()
    user_teams = []
    if request.user.is_authenticated:
        user_liked_ids = set(
            request.user.liked_hackathons.values_list("id", flat=True)
        )
        user_teams = list(request.user.teams_led.all()) + list(request.user.teams_in.all())

    ctx = {
        "hackathons":     hackathons,
        "user_liked_ids": user_liked_ids,
        "user_teams":     user_teams,
    }
    return render(request, "hackathons.html", ctx)


def blogs_view(request):
    """Blogs / feed page."""
    search_query = request.GET.get("q", "").strip()
    active_tag = request.GET.get("tag", "all").strip().lower() or "all"

    base_posts = BlogPost.objects.select_related(
        "author",
        "author__profile",
    ).prefetch_related(
        Prefetch(
            "comments",
            queryset=BlogComment.objects.select_related("author", "author__profile"),
        )
    )
    community_posts_count = base_posts.count()
    posts = base_posts

    # Tag list with counts
    tags = (
        BlogPost.objects.values("tag")
        .annotate(post_count=Count("id"))
        .order_by("-post_count", "tag")
    )

    # Trending: top 3 by likes
    trending_posts = (
        BlogPost.objects.annotate(lc=Count("likes"))
        .order_by("-lc", "-created_at")[:3]
    )

    # Suggested users: 3 users that are NOT the current user
    suggested_users = User.objects.exclude(id=request.user.id).order_by("?")[:3] \
        if request.user.is_authenticated else User.objects.order_by("?")[:3]

    user_liked_post_ids = set()
    user_following_ids  = set()
    user_teams = []
    if request.user.is_authenticated:
        user_liked_post_ids = set(
            request.user.liked_posts.values_list("id", flat=True)
        )
        if hasattr(request.user, "profile"):
            user_following_ids = set(
                request.user.profile.following.values_list("user__id", flat=True)
            )
        user_teams = list(request.user.teams_led.all()) + list(request.user.teams_in.all())

    ctx = {
        "posts":               posts,
        "tags":                tags,
        "total_posts":         community_posts_count,
        "visible_posts_count": community_posts_count,
        "search_query":        search_query,
        "active_tag":          active_tag,
        "trending_posts":      trending_posts,
        "suggested_users":     suggested_users,
        "user_liked_post_ids": user_liked_post_ids,
        "user_following_ids":  user_following_ids,
        "user_teams":          user_teams,
    }
    return render(request, "blogs.html", ctx)


@login_required(login_url="/login/")
def profile_view(request, username=None):
    """
    Profile page.
    /profile/          → logged-in user's own profile
    /profile/<username>/ → any user's profile
    """
    if username:
        profile_user = get_object_or_404(User, username=username)
    else:
        profile_user = request.user

    # Ensure profile exists
    if not hasattr(profile_user, "profile"):
        from .models import Profile
        Profile.objects.get_or_create(user=profile_user)

    user_posts = BlogPost.objects.filter(author=profile_user).order_by("-created_at")
    liked_posts = BlogPost.objects.filter(likes=profile_user).order_by("-created_at")
    user_shared_hackathons = Hackathon.objects.filter(
        posted_by=profile_user, is_approved=True
    ).order_by("-created_at")

    post_count   = user_posts.count()
    total_likes  = sum(p.likes_count for p in user_posts)

    followers_count = profile_user.profile.followers_count
    following_count = profile_user.profile.following_count
    is_following    = False
    if request.user.is_authenticated and hasattr(request.user, "profile"):
        is_following = request.user.profile.following.filter(
            user=profile_user
        ).exists()

    user_liked_post_ids = set()
    if request.user.is_authenticated:
        user_liked_post_ids = set(
            request.user.liked_posts.values_list("id", flat=True)
        )

    # Get user's teams
    user_teams = []
    if request.user.is_authenticated:
        user_teams = list(request.user.teams_led.all()) + list(request.user.teams_in.all())

    ctx = {
        "profile_user":          profile_user,
        "user_posts":            user_posts,
        "liked_posts":           liked_posts,
        "user_shared_hackathons": user_shared_hackathons,
        "post_count":            post_count,
        "total_likes":           total_likes,
        "followers_count":       followers_count,
        "following_count":       following_count,
        "is_following":          is_following,
        "user_liked_post_ids":   user_liked_post_ids,
        "user_teams":            user_teams,
    }
    return render(request, "profile.html", ctx)


# ══════════════════════════════════════════════════════════════════════════════
#  API — BLOGS
# ══════════════════════════════════════════════════════════════════════════════

@login_required(login_url="/login/")
@require_POST
def api_blog_create(request):
    """POST /api/blogs/create/ — Create a new blog post."""
    data    = _json_body(request)
    content = data.get("content", "").strip()
    tag     = data.get("tag", "general").strip().lower()

    if not content:
        return JsonResponse({"error": "Content is required."}, status=400)
    if len(content) > 280:
        return JsonResponse({"error": "Post must be 280 characters or fewer."}, status=400)

    post = BlogPost.objects.create(author=request.user, content=content, tag=tag)
    return JsonResponse({
        "id":              post.id,
        "content":         post.content,
        "tag":             post.tag,
        "author":          request.user.username,
        "author_name":     _display_name(request.user),
        "author_initials": _user_initials(request.user),
        "author_gradient": _user_gradient(request.user),
        "profile_url":     f"/profile/{request.user.username}/",
        "likes_count":     0,
        "comments_count":  0,
        "created_at":      post.created_at.isoformat(),
        "created_label":   "just now",
    }, status=201)


@login_required(login_url="/login/")
@require_POST
def api_blog_like(request, post_id):
    """POST /api/blogs/<post_id>/like/ — Toggle like on a blog post."""
    post = get_object_or_404(BlogPost, id=post_id)

    if post.likes.filter(id=request.user.id).exists():
        post.likes.remove(request.user)
        liked = False
    else:
        post.likes.add(request.user)
        liked = True

    return JsonResponse({"liked": liked, "likes_count": post.likes_count})


@login_required(login_url="/login/")
@require_POST
def api_blog_comment_create(request, post_id):
    """POST /api/blogs/<post_id>/comments/create/ — Create a comment on a blog post."""
    post = get_object_or_404(BlogPost, id=post_id)
    data = _json_body(request)
    content = data.get("content", "").strip()

    if not content:
        return JsonResponse({"error": "Comment content is required."}, status=400)
    if len(content) > 280:
        return JsonResponse({"error": "Comment must be 280 characters or fewer."}, status=400)

    comment = BlogComment.objects.create(post=post, author=request.user, content=content)
    return JsonResponse({
        "id":              comment.id,
        "post_id":         post.id,
        "content":         comment.content,
        "author":          request.user.username,
        "author_name":     _display_name(request.user),
        "author_initials": _user_initials(request.user),
        "author_gradient": _user_gradient(request.user),
        "created_at":      comment.created_at.isoformat(),
        "created_label":   "just now",
        "comments_count":  post.comments.count(),
    }, status=201)


# ══════════════════════════════════════════════════════════════════════════════
#  API — HACKATHONS
# ══════════════════════════════════════════════════════════════════════════════

@login_required(login_url="/login/")
@require_POST
def api_hackathon_create(request):
    """POST /api/hackathons/create/ — Submit a new hackathon (pending approval)."""
    data = _json_body(request)

    required = ["title", "organizer", "description", "registration_link"]
    for field in required:
        if not data.get(field, "").strip():
            return JsonResponse({"error": f"'{field}' is required."}, status=400)

    link = data["registration_link"].strip()
    if not link.startswith("http"):
        return JsonResponse({"error": "Registration link must be a valid URL."}, status=400)

    # Derive initials & colour from organizer name
    org_name     = data["organizer"].strip()
    org_initials = "".join(w[0].upper() for w in org_name.split()[:2]) or org_name[:2].upper()

    hackathon = Hackathon.objects.create(
        title             = data["title"].strip(),
        organizer         = org_name,
        description       = data["description"].strip(),
        status            = data.get("status", "open"),
        location          = data.get("location", "online"),
        month             = int(data.get("month", 3)),
        mode              = data.get("mode", "Online"),
        tags              = data.get("tags", ""),
        registration_link = link,
        org_initials      = org_initials,
        is_approved       = False,   # admin must approve
        posted_by         = request.user,
    )

    return JsonResponse({
        "id":      hackathon.id,
        "title":   hackathon.title,
        "message": "Hackathon submitted! Pending admin review.",
    }, status=201)


@login_required(login_url="/login/")
@require_POST
def api_hackathon_like(request, hackathon_id):
    """POST /api/hackathons/<hackathon_id>/like/ — Toggle like on a hackathon."""
    hackathon = get_object_or_404(Hackathon, id=hackathon_id)

    if hackathon.likes.filter(id=request.user.id).exists():
        hackathon.likes.remove(request.user)
        liked = False
    else:
        hackathon.likes.add(request.user)
        liked = True

    return JsonResponse({"liked": liked, "likes_count": hackathon.likes_count})


# ══════════════════════════════════════════════════════════════════════════════
#  API — USERS / FOLLOW
# ══════════════════════════════════════════════════════════════════════════════

@login_required(login_url="/login/")
@require_POST
def api_user_follow(request, user_id):
    """POST /api/users/<user_id>/follow/ — Toggle follow on a user."""
    target_user = get_object_or_404(User, id=user_id)

    if target_user == request.user:
        return JsonResponse({"error": "You cannot follow yourself."}, status=400)

    # Ensure profiles exist
    from .models import Profile
    my_profile, _ = Profile.objects.get_or_create(user=request.user)
    target_profile, _ = Profile.objects.get_or_create(user=target_user)

    if my_profile.following.filter(user=target_user).exists():
        my_profile.following.remove(target_profile)
        following = False
    else:
        my_profile.following.add(target_profile)
        following = True

    return JsonResponse({
        "following":        following,
        "followers_count":  target_profile.followers_count,
        "following_count":  my_profile.following_count,
        "is_following":     following,
    })


# ══════════════════════════════════════════════════════════════════════════════
#  API — PROFILE UPDATE
# ══════════════════════════════════════════════════════════════════════════════

@login_required(login_url="/login/")
@require_http_methods(["PATCH", "POST"])
def api_profile_update(request):
    """PATCH /api/profile/update/ — Update the current user's profile."""
    data = _json_body(request)

    user    = request.user
    profile = user.profile

    # Update Django User fields
    if "first_name" in data:
        user.first_name = data["first_name"].strip()
    if "last_name" in data:
        user.last_name = data["last_name"].strip()
    user.save(update_fields=["first_name", "last_name"])

    # Update Profile fields
    if "bio" in data:
        profile.bio = data["bio"].strip()
    if "college" in data:
        profile.college = data["college"].strip()
    if "location" in data:
        profile.location = data["location"].strip()
    if "skills" in data:
        skills = data["skills"]
        # Accept either a list or a comma-separated string
        if isinstance(skills, list):
            profile.skills = ",".join(s.strip() for s in skills if s.strip())
        else:
            profile.skills = skills.strip()

    profile.save()

    return JsonResponse({
        "success":    True,
        "first_name": user.first_name,
        "last_name":  user.last_name,
        "bio":        profile.bio,
        "college":    profile.college,
        "location":   profile.location,
        "skills":     profile.skills_list,
    })


# ══════════════════════════════════════════════════════════════════════════════
#  TEAM RECRUITMENT
# ══════════════════════════════════════════════════════════════════════════════

def team_recruit_view(request):
    """Team recruitment hub - browse and manage teams."""
    search_query = request.GET.get("q", "").strip()
    category_filter = request.GET.get("category", "all").strip()
    status_filter = request.GET.get("status", "recruiting").strip()

    teams = Team.objects.select_related("leader", "leader__profile").prefetch_related("members")

    if search_query:
        teams = teams.filter(name__icontains=search_query) | teams.filter(description__icontains=search_query)

    if category_filter and category_filter != "all":
        teams = teams.filter(category=category_filter)

    if status_filter and status_filter != "all":
        teams = teams.filter(status=status_filter)

    teams = teams.order_by("-created_at")

    # User's own teams and invites
    user_teams = []
    pending_invites = []
    if request.user.is_authenticated:
        user_teams = Team.objects.filter(leader=request.user) | Team.objects.filter(members=request.user)
        user_teams = user_teams.distinct()
        pending_invites = TeamInvite.objects.filter(user=request.user, status="pending").select_related("team", "team__leader")

    ctx = {
        "teams":             teams,
        "search_query":      search_query,
        "category_filter":   category_filter,
        "status_filter":     status_filter,
        "user_teams":        user_teams,
        "pending_invites":   pending_invites,
        "category_choices":  Team.CATEGORY_CHOICES,
    }
    return render(request, "Team_recruit.html", ctx)


@login_required(login_url="/login/")
def team_detail_view(request, team_id):
    """View a specific team's details."""
    team = get_object_or_404(Team, id=team_id)
    members = team.members.all()
    is_leader = request.user == team.leader
    is_member = request.user in members
    has_pending_invite = TeamInvite.objects.filter(team=team, user=request.user, status="pending").exists()

    ctx = {
        "team":               team,
        "members":            members,
        "is_leader":          is_leader,
        "is_member":          is_member,
        "has_pending_invite": has_pending_invite,
    }
    return render(request, "team_detail.html", ctx)


@login_required(login_url="/login/")
@require_POST
def api_team_create(request):
    """POST /api/teams/create/ — Create a new team."""
    data = _json_body(request)
    
    name = data.get("name", "").strip()
    description = data.get("description", "").strip()
    category = data.get("category", "other").strip()
    members_needed = data.get("members_needed", 2)
    skills_required = data.get("skills_required", "").strip()

    if not name:
        return JsonResponse({"error": "Team name is required."}, status=400)
    if not description:
        return JsonResponse({"error": "Description is required."}, status=400)
    if len(name) > 200:
        return JsonResponse({"error": "Team name must be 200 characters or fewer."}, status=400)

    team = Team.objects.create(
        name=name,
        description=description,
        category=category,
        members_needed=members_needed,
        skills_required=skills_required,
        leader=request.user,
        status="recruiting"
    )

    return JsonResponse({
        "id":           team.id,
        "name":         team.name,
        "description":  team.description,
        "category":     team.category,
        "status":       team.status,
        "members_count": team.members_count,
        "open_slots":   team.open_slots,
        "created_at":   team.created_at.isoformat(),
    }, status=201)


@login_required(login_url="/login/")
@require_POST
def api_team_invite(request, team_id):
    """POST /api/teams/<team_id>/invite/ — Invite a user to a team."""
    team = get_object_or_404(Team, id=team_id)
    data = _json_body(request)
    
    username = data.get("username", "").strip()
    message = data.get("message", "Join our team!").strip()

    if request.user != team.leader:
        return JsonResponse({"error": "Only team leaders can invite members."}, status=403)

    if not username:
        return JsonResponse({"error": "Username is required."}, status=400)

    invite_user = get_object_or_404(User, username=username)

    if invite_user == team.leader:
        return JsonResponse({"error": "Cannot invite the team leader."}, status=400)

    if invite_user in team.members.all():
        return JsonResponse({"error": "User is already a member."}, status=400)

    if TeamInvite.objects.filter(team=team, user=invite_user).exists():
        return JsonResponse({"error": "Invite already sent to this user."}, status=400)

    invite = TeamInvite.objects.create(team=team, user=invite_user, message=message)

    return JsonResponse({
        "id":           invite.id,
        "team_id":      team.id,
        "user":         invite_user.username,
        "status":       invite.status,
        "message":      invite.message,
        "created_at":   invite.created_at.isoformat(),
    }, status=201)


@login_required(login_url="/login/")
@require_POST
def api_team_invite_respond(request, invite_id):
    """POST /api/teams/invites/<invite_id>/respond/ — Accept or decline a team invite."""
    invite = get_object_or_404(TeamInvite, id=invite_id)
    data = _json_body(request)
    
    action = data.get("action", "").strip().lower()

    if request.user != invite.user:
        return JsonResponse({"error": "You can only respond to invites sent to you."}, status=403)

    if invite.status != "pending":
        return JsonResponse({"error": f"Invite is already {invite.status}."}, status=400)

    if action == "accept":
        if invite.team.open_slots <= 0:
            return JsonResponse({"error": "Team is full."}, status=400)

        invite.status = "accepted"
        invite.save()
        TeamMember.objects.create(team=invite.team, user=request.user, role="other")
        
        return JsonResponse({
            "status":     "accepted",
            "message":    "Welcome to the team!",
            "team_name":  invite.team.name,
        })

    elif action == "decline":
        invite.status = "declined"
        invite.save()
        
        return JsonResponse({
            "status":  "declined",
            "message": "Invite declined.",
        })

    return JsonResponse({"error": "Invalid action. Use 'accept' or 'decline'."}, status=400)


@login_required(login_url="/login/")
@require_POST
def api_team_remove_member(request, team_id):
    """POST /api/teams/<team_id>/remove-member/ — Remove a member from team."""
    team = get_object_or_404(Team, id=team_id)
    data = _json_body(request)
    
    member_id = data.get("member_id")

    if request.user != team.leader:
        return JsonResponse({"error": "Only team leaders can remove members."}, status=403)

    member = get_object_or_404(User, id=member_id)
    member_record = TeamMember.objects.filter(team=team, user=member)

    if not member_record.exists():
        return JsonResponse({"error": "User is not a member of this team."}, status=400)

    member_record.delete()

    return JsonResponse({
        "success":      True,
        "message":      f"{member.username} has been removed from the team.",
        "remaining":    team.members_count - 1,
    })


@login_required(login_url="/login/")
@require_POST
def api_team_update_status(request, team_id):
    """POST /api/teams/<team_id>/update-status/ — Update team status (recruiting/full/closed)."""
    team = get_object_or_404(Team, id=team_id)
    data = _json_body(request)
    
    status = data.get("status", "").strip().lower()

    if request.user != team.leader:
        return JsonResponse({"error": "Only team leaders can update team status."}, status=403)

    valid_statuses = ["recruiting", "full", "closed"]
    if status not in valid_statuses:
        return JsonResponse({"error": f"Status must be one of: {', '.join(valid_statuses)}"}, status=400)

    team.status = status
    team.save(update_fields=["status"])

    return JsonResponse({
        "success": True,
        "status":  team.status,
        "message": f"Team status updated to '{status}'.",
    })
