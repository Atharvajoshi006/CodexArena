import json
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST, require_http_methods
from django.http import JsonResponse
from django.db.models import Count
from django.contrib import messages

from .models import Profile, BlogPost, BlogComment, Hackathon


# ══════════════════════════════════════════════════════════════════════════════
#  HELPER
# ══════════════════════════════════════════════════════════════════════════════

def _json_body(request):
    """Parse JSON request body safely."""
    try:
        return json.loads(request.body)
    except (json.JSONDecodeError, ValueError):
        return {}


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

    ctx = {
        "featured_hackathons": featured_hackathons,
        "recent_blogs":        recent_blogs,
        "hackathon_count":     hackathon_count,
        "user_count":          user_count,
    }
    return render(request, "index.html", ctx)


def hackathons_view(request):
    """Hackathons listing page."""
    hackathons = Hackathon.objects.filter(is_approved=True).order_by("-is_featured", "-created_at")

    # Pass IDs the current user has liked (for button state)
    user_liked_ids = set()
    if request.user.is_authenticated:
        user_liked_ids = set(
            request.user.liked_hackathons.values_list("id", flat=True)
        )

    ctx = {
        "hackathons":     hackathons,
        "user_liked_ids": user_liked_ids,
    }
    return render(request, "hackathons.html", ctx)


def blogs_view(request):
    """Blogs / feed page."""
    posts = BlogPost.objects.select_related("author", "author__profile").all()

    # Tag list with counts
    tags = (
        BlogPost.objects.values("tag")
        .annotate(post_count=Count("id"))
        .order_by("-post_count")
    )

    # Trending: top 3 by likes
    trending_posts = (
        BlogPost.objects.annotate(lc=Count("likes"))
        .order_by("-lc")[:3]
    )

    # Suggested users: 3 users that are NOT the current user
    suggested_users = User.objects.exclude(id=request.user.id).order_by("?")[:3] \
        if request.user.is_authenticated else User.objects.order_by("?")[:3]

    user_liked_post_ids = set()
    user_following_ids  = set()
    if request.user.is_authenticated:
        user_liked_post_ids = set(
            request.user.liked_posts.values_list("id", flat=True)
        )
        if hasattr(request.user, "profile"):
            user_following_ids = set(
                request.user.profile.following.values_list("user__id", flat=True)
            )

    ctx = {
        "posts":               posts,
        "tags":                tags,
        "total_posts":         posts.count(),
        "trending_posts":      trending_posts,
        "suggested_users":     suggested_users,
        "user_liked_post_ids": user_liked_post_ids,
        "user_following_ids":  user_following_ids,
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

    user_posts = BlogPost.objects.filter(author=profile_user).order_by("-created_at")
    liked_posts = BlogPost.objects.filter(likes=profile_user).order_by("-created_at")
    user_shared_hackathons = Hackathon.objects.filter(
        posted_by=profile_user, is_approved=True
    ).order_by("-created_at")

    post_count   = user_posts.count()
    total_likes  = sum(p.likes_count for p in user_posts)

    followers_count = 0
    following_count = 0
    is_following    = False
    if hasattr(profile_user, "profile"):
        followers_count = profile_user.profile.followers_count
        following_count = profile_user.profile.following_count
        if request.user.is_authenticated and hasattr(request.user, "profile"):
            is_following = request.user.profile.following.filter(
                user=profile_user
            ).exists()

    user_liked_post_ids = set()
    if request.user.is_authenticated:
        user_liked_post_ids = set(
            request.user.liked_posts.values_list("id", flat=True)
        )

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
        "id":         post.id,
        "content":    post.content,
        "tag":        post.tag,
        "author":     request.user.username,
        "likes_count": 0,
        "created_at": post.created_at.isoformat(),
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

    my_profile     = request.user.profile
    target_profile = target_user.profile

    if my_profile.following.filter(user=target_user).exists():
        my_profile.following.remove(target_profile)
        following = False
    else:
        my_profile.following.add(target_profile)
        following = True

    return JsonResponse({
        "following":        following,
        "followers_count":  target_profile.followers_count,
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