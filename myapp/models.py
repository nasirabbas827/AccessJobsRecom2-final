from django.db import models
from django.utils import timezone

# ------------------------
# Choices
# ------------------------

STATUS_CHOICES = (
    ('pending', 'Pending'),
    ('approved', 'Approved'),
    ('rejected', 'Rejected'),
)

JOB_TYPE_CHOICES = (
    ('full_time', 'Full Time'),
    ('part_time', 'Part Time'),
    ('remote', 'Remote'),
    ('contract', 'Contract'),
    ('internship', 'Internship'),
)

APPLICATION_STATUS = (
    ('applied', 'Applied'),
    ('in_review', 'In Review'),
    ('shortlisted', 'Shortlisted'),
    ('rejected', 'Rejected'),
    ('hired', 'Hired'),
)


# ------------------------
# Job Seeker Model
# ------------------------

class JobSeeker(models.Model):
    full_name = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    password = models.CharField(max_length=255)  # hashed in practice
    phone_number = models.CharField(max_length=20)
    location = models.CharField(max_length=100)
    education = models.TextField()
    work_experience = models.TextField()
    skills = models.TextField()  # comma-separated or JSON
    certificate = models.TextField()
    job_type = models.CharField(max_length=20, choices=JOB_TYPE_CHOICES, default='full_time')
    professional_references = models.TextField(blank=True, null=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='approved')
    profile_picture = models.ImageField(upload_to='profile_pics/', null=True, blank=True)
    resume = models.FileField(upload_to='resumes/', null=True, blank=True)  # PDF/Word upload

    def __str__(self):
        return self.full_name


# ------------------------
# Job Model
# ------------------------

class Job(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField()
    company_name = models.CharField(max_length=200, blank=True, null=True)
    location = models.CharField(max_length=150, blank=True, null=True)
    job_type = models.CharField(max_length=20, choices=JOB_TYPE_CHOICES, default='full_time')
    salary_range = models.CharField(max_length=100, blank=True, null=True)
    required_skills = models.TextField()  # comma-separated skills
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.title} at {self.company_name}"


# ------------------------
# Bookmark Model
# ------------------------

class Bookmark(models.Model):
    job_seeker = models.ForeignKey(JobSeeker, on_delete=models.CASCADE, related_name="bookmarks")
    job = models.ForeignKey(Job, on_delete=models.CASCADE, related_name="bookmarked_by")
    saved_at = models.DateTimeField(default=timezone.now)

    class Meta:
        unique_together = ('job_seeker', 'job')  # prevent duplicate bookmarks

    def __str__(self):
        return f"{self.job_seeker.full_name} bookmarked {self.job.title}"


# ------------------------
# Application Model
# ------------------------

class Application(models.Model):
    job_seeker = models.ForeignKey(JobSeeker, on_delete=models.CASCADE, related_name="applications")
    job = models.ForeignKey(Job, on_delete=models.CASCADE, related_name="applications")
    status = models.CharField(max_length=20, choices=APPLICATION_STATUS, default='applied')
    applied_at = models.DateTimeField(default=timezone.now)

    class Meta:
        unique_together = ('job_seeker', 'job')  # prevent multiple applications for same job

    def __str__(self):
        return f"{self.job_seeker.full_name} applied for {self.job.title} ({self.status})"
