from django.contrib import admin
from .models import JobSeeker, Job, Bookmark, Application


# ------------------------
# JobSeeker Admin
# ------------------------
@admin.register(JobSeeker)
class JobSeekerAdmin(admin.ModelAdmin):
    list_display = (
        "full_name", "email", "phone_number", "location",
        "job_type", "status"
    )
    list_filter = ("status", "job_type", "location")
    search_fields = ("full_name", "email", "skills", "location")
    ordering = ("-id",)
    readonly_fields = ("profile_picture", "resume")

    # Admin actions
    actions = ["approve_users", "reject_users", "set_pending"]

    def approve_users(self, request, queryset):
        queryset.update(status="approved")
        self.message_user(request, "Selected job seekers have been approved.")
    approve_users.short_description = "Approve selected job seekers"

    def reject_users(self, request, queryset):
        queryset.update(status="rejected")
        self.message_user(request, "Selected job seekers have been rejected.")
    reject_users.short_description = "Reject selected job seekers"

    def set_pending(self, request, queryset):
        queryset.update(status="pending")
        self.message_user(request, "Selected job seekers set to pending.")
    set_pending.short_description = "Mark selected job seekers as Pending"


# ------------------------
# Job Admin
# ------------------------
@admin.register(Job)
class JobAdmin(admin.ModelAdmin):
    list_display = ("title", "company_name", "job_type", "location", "salary_range", "created_at")
    list_filter = ("job_type", "location", "company_name")
    search_fields = ("title", "company_name", "description", "required_skills")
    ordering = ("-created_at",)


# ------------------------
# Bookmark Admin
# ------------------------
@admin.register(Bookmark)
class BookmarkAdmin(admin.ModelAdmin):
    list_display = ("job_seeker", "job", "saved_at")
    list_filter = ("saved_at",)
    search_fields = ("job_seeker__full_name", "job__title")
    ordering = ("-saved_at",)


# ------------------------
# Application Admin
# ------------------------
@admin.register(Application)
class ApplicationAdmin(admin.ModelAdmin):
    list_display = ("job_seeker", "job", "status", "applied_at")
    list_filter = ("status", "applied_at")
    search_fields = ("job_seeker__full_name", "job__title")
    ordering = ("-applied_at",)
