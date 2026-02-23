from django.urls import path
from . import views
from .views_applied import applied_companies

app_name = "application"

urlpatterns = [
    path("apply/", views.apply_for_job, name="apply"),
    path("apply/<int:job_id>/", views.apply_for_job, name="apply_job"),
    path('applied/', applied_companies, name='applied_companies'),
    path('apply/', applied_companies, name='apply_companies'),
]