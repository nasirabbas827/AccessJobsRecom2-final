from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.hashers import check_password
from django.contrib.auth import login as auth_login, logout as auth_logout
from django.contrib.sessions.models import Session
from django.utils import timezone
from .forms import JobSeekerRegisterForm
from .models import JobSeeker, JOB_TYPE_CHOICES , Bookmark


# ------------------------
# Index View
# ------------------------
def index(request):
    return render(request, 'index.html')


# ------------------------
# Register View 
# ------------------------
def register_view(request):
    if request.method == 'POST':
        form = JobSeekerRegisterForm(request.POST, request.FILES)
        if form.is_valid():
            jobseeker = form.save(commit=False)
            jobseeker.status = 'approved'   
            jobseeker.save()
            messages.success(request, 'Registration successful! Please wait for admin approval.')
            return redirect('login')
    else:
        form = JobSeekerRegisterForm()
    return render(request, 'register.html', {'form': form})


# ------------------------
# Login View (Check Approved)
# ------------------------
def login_view(request):
    if request.method == 'POST':
        email = request.POST.get('email').lower()
        password = request.POST.get('password')
        try:
            user = JobSeeker.objects.get(email=email)

            if user.status != 'approved':
                messages.warning(request, "Your account is not approved yet. Please wait for admin approval.")
            elif check_password(password, user.password):
                request.session['jobseeker_id'] = user.id
                messages.success(request, f"Welcome, {user.full_name}")
                return redirect('dashboard')
            else:
                messages.error(request, "Invalid password.")
        except JobSeeker.DoesNotExist:
            messages.error(request, "Account not found.")
    return render(request, 'login.html')


from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.db.models import Q
from django.contrib.auth import logout as auth_logout
from .models import JobSeeker, Job, Application
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.db.models import Q
from django.contrib.auth import logout as auth_logout
from .models import JobSeeker, Job, Application
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np
from datetime import timedelta
from django.utils import timezone

# ------------------------
# Dashboard
# ------------------------
def dashboard_view(request):
    jobseeker_id = request.session.get("jobseeker_id")
    if not jobseeker_id:
        messages.warning(request, "Please log in to access the dashboard.")
        return redirect("login")

    jobseeker = JobSeeker.objects.get(id=jobseeker_id)

    # ------------------------
    # Filters
    # ------------------------
    keyword = request.GET.get("keyword", "")
    location = request.GET.get("location", "")
    job_type = request.GET.get("job_type", "")
    salary = request.GET.get("salary", "")

    jobs = Job.objects.all()

    if keyword:
        jobs = jobs.filter(
            Q(title__icontains=keyword) |
            Q(description__icontains=keyword) |
            Q(required_skills__icontains=keyword)
        )

    if location:
        jobs = jobs.filter(location__icontains=location)

    if job_type:
        jobs = jobs.filter(job_type=job_type)

    if salary:
        jobs = jobs.filter(salary_range__icontains=salary)

    # ------------------------
    # Content-Based Filtering for Recommended Jobs
    # ------------------------
    seeker_profile = (
        f"{jobseeker.skills} {jobseeker.education} {jobseeker.work_experience} {jobseeker.job_type}"
    ).lower()

    jobs_list = list(jobs)
    job_texts = [
        f"{job.required_skills} {job.description} {job.job_type}".lower()
        for job in jobs_list
    ]

    recommended_jobs = Job.objects.none()
    match_scores = {}
    if job_texts:
        all_texts = [seeker_profile] + job_texts
        vectorizer = TfidfVectorizer(stop_words='english')
        tfidf_matrix = vectorizer.fit_transform(all_texts)
        cosine_similarities = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:]).flatten()
        job_indices = np.argsort(cosine_similarities)[::-1]
        recommended_job_ids = [
            jobs_list[int(i)].id for i in job_indices[:5] if cosine_similarities[i] > 0
        ]
        match_scores = {
            jobs_list[int(i)].id: round(cosine_similarities[i] * 100, 1)
            for i in job_indices[:5] if cosine_similarities[i] > 0
        }
        recommended_jobs = jobs.filter(id__in=recommended_job_ids)
        recommended_jobs = sorted(
            recommended_jobs,
            key=lambda x: job_indices[jobs_list.index(x)] if x in jobs_list else -1,
            reverse=True
        )

    # ------------------------
    # Job Alerts & Notifications
    # ------------------------
    recent_jobs = Job.objects.filter(
        created_at__gte=timezone.now() - timedelta(days=7)
    ).order_by('-created_at')[:5]

    context = {
        "jobseeker": jobseeker,
        "jobs": jobs,
        "recommended_jobs": recommended_jobs,
        "match_scores": match_scores,
        "recent_jobs": recent_jobs,
    }
    return render(request, "dashboard.html", context)

# ------------------------
# Job Detail
# ------------------------
def job_detail_view(request, job_id):
    jobseeker_id = request.session.get("jobseeker_id")
    if not jobseeker_id:
        messages.warning(request, "Please log in to view job details.")
        return redirect("login")

    job = get_object_or_404(Job, id=job_id)
    jobseeker = JobSeeker.objects.get(id=jobseeker_id)

    # For toggling bookmark state in template
    bookmarked_jobs = Bookmark.objects.filter(job_seeker=jobseeker).values_list("job_id", flat=True)

    return render(request, "job_detail.html", {
        "job": job,
        "bookmarked_jobs": bookmarked_jobs,
    })


# ------------------------
# Apply Job
# ------------------------
def apply_job(request, job_id):
    jobseeker_id = request.session.get("jobseeker_id")
    if not jobseeker_id:
        messages.warning(request, "Please log in to apply for jobs.")
        return redirect("login")

    job = get_object_or_404(Job, id=job_id)
    jobseeker = JobSeeker.objects.get(id=jobseeker_id)

    Application.objects.get_or_create(
        job_seeker=jobseeker,
        job=job,
        defaults={"status": "applied"}
    )
    messages.success(request, "Your application has been submitted!")
    return redirect("job_detail", job_id=job.id)


# ------------------------
# Toggle Bookmark
# ------------------------
def toggle_bookmark(request, job_id):
    jobseeker_id = request.session.get("jobseeker_id")
    if not jobseeker_id:
        messages.warning(request, "Please log in to bookmark jobs.")
        return redirect("login")

    job = get_object_or_404(Job, id=job_id)
    jobseeker = JobSeeker.objects.get(id=jobseeker_id)

    bookmark, created = Bookmark.objects.get_or_create(job_seeker=jobseeker, job=job)
    if not created:
        bookmark.delete()
        messages.info(request, "Bookmark removed.")
    else:
        messages.success(request, "Job bookmarked!")
    return redirect("job_detail", job_id=job.id)


# ------------------------
# Bookmarked Jobs
# ------------------------
def bookmarked_jobs(request):
    jobseeker_id = request.session.get("jobseeker_id")
    if not jobseeker_id:
        messages.warning(request, "Please log in to view bookmarked jobs.")
        return redirect("login")

    jobseeker = JobSeeker.objects.get(id=jobseeker_id)
    bookmarks = Bookmark.objects.filter(job_seeker=jobseeker).select_related("job")

    return render(request, "bookmarked_jobs.html", {"bookmarks": bookmarks})


# ------------------------
# Application Tracking
# ------------------------
def application_tracking(request):
    jobseeker_id = request.session.get("jobseeker_id")
    if not jobseeker_id:
        messages.warning(request, "Please log in to track your applications.")
        return redirect("login")

    jobseeker = JobSeeker.objects.get(id=jobseeker_id)
    applications = Application.objects.filter(job_seeker=jobseeker).select_related("job")

    return render(request, "application_tracking.html", {"applications": applications})


# ------------------------
# Logout
# ------------------------
def logout_view(request):
    auth_logout(request)
    request.session.flush()
    messages.warning(request, "You have been logged out.")
    return redirect('login')

# ------------------------
# Update Profile
# ------------------------
def update_profile_view(request):
    jobseeker_id = request.session.get('jobseeker_id')
    if not jobseeker_id:
        messages.error(request, "Please log in to update your profile.")
        return redirect('login')

    jobseeker = JobSeeker.objects.get(id=jobseeker_id)

    if request.method == 'POST':
        jobseeker.full_name = request.POST.get('full_name')
        jobseeker.email = request.POST.get('email')
        jobseeker.phone_number = request.POST.get('phone_number')
        jobseeker.location = request.POST.get('location')
        jobseeker.education = request.POST.get('education')
        jobseeker.work_experience = request.POST.get('work_experience')
        jobseeker.skills = request.POST.get('skills')
        jobseeker.certificate = request.POST.get('certificate')
        jobseeker.job_type = request.POST.get('job_type')
        jobseeker.professional_references = request.POST.get('professional_references')

        if 'profile_picture' in request.FILES:
            jobseeker.profile_picture = request.FILES['profile_picture']
        if 'resume' in request.FILES:
            jobseeker.resume = request.FILES['resume']

        jobseeker.save()
        messages.success(request, "Profile updated successfully.")
        return redirect('update_profile')

    return render(request, 'update_profile.html', {
        'jobseeker': jobseeker,
        'job_type_choices': JOB_TYPE_CHOICES
    })
