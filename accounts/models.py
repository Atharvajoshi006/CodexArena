from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone


# ─── USER PROFILE ────────────────────────────────────────────────────────────

class Profile(models.Model):
    user       = models.OneToOneField(User, on_delete=models.CASCADE, related_name="profile")
    bio        = models.TextField(blank=True, default="")
    college    = models.CharField(max_length=200, blank=True, default="")
    location   = models.CharField(max_length=200, blank=True, default="")
    skills     = models.CharField(max_length=500, blank=True, default="")   # comma-separated
    avatar     = models.ImageField(upload_to="avatars/", blank=True, null=True)
    banner     = models.ImageField(upload_to="banners/", blank=True, null=True)
    # gradient colour string used when no avatar uploaded, e.g. "linear-gradient(135deg,#2f81f7,#58a6ff)"
    avatar_gradient = models.CharField(max_length=120, blank=True, default="linear-gradient(135deg,#2f81f7,#58a6ff)")

    # Follow relationships
    following  = models.ManyToManyField("self", symmetrical=False, blank=True, related_name="followers")

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.username}'s profile"

    @property
    def skills_list(self):
        """Return skills as a Python list."""
        return [s.strip() for s in self.skills.split(",") if s.strip()]

    @property
    def followers_count(self):
        return self.followers.count()

    @property
    def following_count(self):
        return self.following.count()


# ─── BLOG POST ────────────────────────────────────────────────────────────────

class BlogPost(models.Model):
    author     = models.ForeignKey(User, on_delete=models.CASCADE, related_name="blog_posts")
    content    = models.TextField(max_length=280)
    tag        = models.CharField(max_length=50, default="general")
    likes      = models.ManyToManyField(User, blank=True, related_name="liked_posts")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.author.username}: {self.content[:60]}"

    @property
    def likes_count(self):
        return self.likes.count()

    @property
    def comments_count(self):
        return self.comments.count()


class BlogComment(models.Model):
    post       = models.ForeignKey(BlogPost, on_delete=models.CASCADE, related_name="comments")
    author     = models.ForeignKey(User, on_delete=models.CASCADE, related_name="blog_comments")
    content    = models.TextField(max_length=280)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["created_at"]

    def __str__(self):
        return f"{self.author.username} on post {self.post.id}"


# ─── HACKATHON ────────────────────────────────────────────────────────────────

class Hackathon(models.Model):
    STATUS_CHOICES = [
        ("open",     "◉ Open"),
        ("upcoming", "◈ Upcoming"),
        ("closing",  "⚡ Closing Soon"),
        ("trending", "▲ Trending"),
    ]
    LOCATION_CHOICES = [
        ("online",     "🌐 Online"),
        ("bengaluru",  "Bengaluru"),
        ("mumbai",     "Mumbai"),
        ("delhi",      "Delhi"),
        ("hyderabad",  "Hyderabad"),
        ("chennai",    "Chennai"),
        ("pune",       "Pune"),
        ("varanasi",   "Varanasi"),
        ("coimbatore", "Coimbatore"),
    ]

    title             = models.CharField(max_length=200)
    organizer         = models.CharField(max_length=200)
    description       = models.TextField()
    status            = models.CharField(max_length=20, choices=STATUS_CHOICES, default="open")
    location          = models.CharField(max_length=30, choices=LOCATION_CHOICES, default="online")
    month             = models.PositiveSmallIntegerField(default=3)  # 1-12
    mode              = models.CharField(max_length=20, default="Online",
                                         choices=[("Online","Online"),("In-Person","In-Person"),("Hybrid","Hybrid")])
    tags              = models.CharField(max_length=300, blank=True, default="")  # comma-separated
    registration_link = models.URLField(max_length=500)
    org_color         = models.CharField(max_length=20, default="#2f81f7")
    org_initials      = models.CharField(max_length=5, default="ORG")
    is_featured       = models.BooleanField(default=False)
    is_approved       = models.BooleanField(default=False)  # admin approves community submissions

    posted_by         = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name="shared_hackathons")
    likes             = models.ManyToManyField(User, blank=True, related_name="liked_hackathons")
    created_at        = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-is_featured", "-created_at"]

    def __str__(self):
        return self.title

    @property
    def likes_count(self):
        return self.likes.count()

    @property
    def tags_list(self):
        return [t.strip() for t in self.tags.split(",") if t.strip()]

    @property
    def location_display(self):
        return dict(self.LOCATION_CHOICES).get(self.location, self.location)

    @property
    def month_year(self):
        months = ["", "Jan", "Feb", "Mar", "Apr", "May", "Jun",
                  "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
        return f"{months[self.month]} 2026"

    @property
    def source_label(self):
        link = self.registration_link.lower()
        if "devfolio" in link:
            return "Register on Devfolio →"
        elif "unstop" in link:
            return "Register on Unstop →"
        elif "devpost" in link:
            return "Register on Devpost →"
        return "Register →"

    @property
    def posted_by_initials(self):
        if self.posted_by:
            name = self.posted_by.get_full_name() or self.posted_by.username
            parts = name.split()
            return (parts[0][0] + parts[1][0]).upper() if len(parts) > 1 else name[:2].upper()
        return "CA"

    @property
    def posted_by_username(self):
        return f"@{self.posted_by.username}" if self.posted_by else "@codexarena"

    @property
    def posted_by_color(self):
        return getattr(self.posted_by, "profile", None) and self.posted_by.profile.avatar_gradient or "linear-gradient(135deg,#2f81f7,#58a6ff)"


# ─── TEAM RECRUITMENT ─────────────────────────────────────────────────────────

class Team(models.Model):
    STATUS_CHOICES = [
        ("recruiting", "🔍 Recruiting"),
        ("full",       "✓ Full"),
        ("closed",     "✕ Closed"),
    ]
    CATEGORY_CHOICES = [
        ("web",      "Web Development"),
        ("mobile",   "Mobile App"),
        ("ai-ml",    "AI/ML"),
        ("backend",  "Backend"),
        ("devops",   "DevOps"),
        ("design",   "Design"),
        ("other",    "Other"),
    ]

    name             = models.CharField(max_length=200)
    description      = models.TextField()
    category         = models.CharField(max_length=30, choices=CATEGORY_CHOICES, default="other")
    status           = models.CharField(max_length=15, choices=STATUS_CHOICES, default="recruiting")
    skills_required  = models.CharField(max_length=500, blank=True, default="")  # comma-separated
    members_needed   = models.PositiveSmallIntegerField(default=2, help_text="Target team size")
    
    leader           = models.ForeignKey(User, on_delete=models.CASCADE, related_name="teams_led")
    members          = models.ManyToManyField(User, blank=True, related_name="teams_in", through="TeamMember")
    pending_invites  = models.ManyToManyField(User, blank=True, related_name="team_invites", through="TeamInvite")
    
    created_at       = models.DateTimeField(auto_now_add=True)
    updated_at       = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return self.name

    @property
    def members_count(self):
        return self.members.count() + 1  # +1 for leader

    @property
    def skills_list(self):
        return [s.strip() for s in self.skills_required.split(",") if s.strip()]

    @property
    def open_slots(self):
        return max(0, self.members_needed - self.members_count)


class TeamMember(models.Model):
    ROLE_CHOICES = [
        ("backend",  "Backend Developer"),
        ("frontend", "Frontend Developer"),
        ("fullstack","Full-Stack Developer"),
        ("design",   "Designer"),
        ("devops",   "DevOps Engineer"),
        ("ml",       "ML Engineer"),
        ("other",    "Other"),
    ]

    team       = models.ForeignKey(Team, on_delete=models.CASCADE, related_name="member_records")
    user       = models.ForeignKey(User, on_delete=models.CASCADE, related_name="team_roles")
    role       = models.CharField(max_length=20, choices=ROLE_CHOICES, default="other")
    joined_at  = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("team", "user")
        ordering = ["joined_at"]

    def __str__(self):
        return f"{self.user.username} in {self.team.name}"


class TeamInvite(models.Model):
    STATUS_CHOICES = [
        ("pending",  "Pending"),
        ("accepted", "Accepted"),
        ("declined", "Declined"),
    ]

    team       = models.ForeignKey(Team, on_delete=models.CASCADE, related_name="invite_records")
    user       = models.ForeignKey(User, on_delete=models.CASCADE, related_name="received_invites")
    status     = models.CharField(max_length=10, choices=STATUS_CHOICES, default="pending")
    message    = models.TextField(blank=True, default="Join our team!")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ("team", "user")
        ordering = ["-created_at"]

    def __str__(self):
        return f"Invite from {self.team.name} to {self.user.username}"