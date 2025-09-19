from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('', views.index, name='index'),
    path('register/', views.register_view, name='register'),
    path('login/', views.login_view, name='login'),
    path('dashboard/', views.dashboard_view, name='dashboard'),
    path("job/<int:job_id>/", views.job_detail_view, name="job_detail"),
    path('logout/', views.logout_view, name='logout'),
    path('update-profile/', views.update_profile_view, name='update_profile'),
    path("job/<int:job_id>/apply/", views.apply_job, name="apply_job"),
    path("job/<int:job_id>/bookmark/", views.toggle_bookmark, name="toggle_bookmark"),
    path("bookmarked-jobs/", views.bookmarked_jobs, name="bookmarked_jobs"),
    path("application-tracking/", views.application_tracking, name="application_tracking"),

]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
