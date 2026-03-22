from django.contrib import admin
from django.contrib.auth.models import User
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import Profile, BlogPost, BlogComment, Hackathon


# ─── PROFILE INLINE ──────────────────────────────────────────────────────────

class ProfileInline(admin.StackedInline):
    model   = Profile
    can_delete = False
    verbose_name_plural = "Profile"
    fields  = ("bio", "college", "location", "skills", "avatar", "avatar_gradient")


class UserAdmin(BaseUserAdmin):
    inlines = (ProfileInline,)


admin.site.unregister(User)
admin.site.register(User, UserAdmin)


# ─── PROFILE ─────────────────────────────────────────────────────────────────

@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display  = ("user", "college", "location", "followers_count", "following_count")
    search_fields = ("user__username", "college", "location")
    readonly_fields = ("created_at", "updated_at")


# ─── BLOG POST ───────────────────────────────────────────────────────────────

@admin.register(BlogPost)
class BlogPostAdmin(admin.ModelAdmin):
    list_display  = ("author", "tag", "likes_count", "comments_count", "created_at", "short_content")
    list_filter   = ("tag", "created_at")
    search_fields = ("author__username", "content", "tag")
    readonly_fields = ("created_at",)

    def short_content(self, obj):
        return obj.content[:80]
    short_content.short_description = "Content"


@admin.register(BlogComment)
class BlogCommentAdmin(admin.ModelAdmin):
    list_display  = ("author", "post", "created_at")
    search_fields = ("author__username", "content")


# ─── HACKATHON ───────────────────────────────────────────────────────────────

@admin.register(Hackathon)
class HackathonAdmin(admin.ModelAdmin):
    list_display  = ("title", "organizer", "status", "location", "month", "is_featured", "is_approved", "likes_count", "created_at")
    list_filter   = ("status", "location", "is_featured", "is_approved", "month")
    search_fields = ("title", "organizer", "description", "tags")
    list_editable = ("is_featured", "is_approved")
    readonly_fields = ("created_at",)
    fieldsets = (
        ("Basic Info", {
            "fields": ("title", "organizer", "description", "registration_link")
        }),
        ("Details", {
            "fields": ("status", "location", "month", "mode", "tags")
        }),
        ("Display", {
            "fields": ("org_color", "org_initials", "is_featured", "is_approved")
        }),
        ("Meta", {
            "fields": ("posted_by", "created_at")
        }),
    )