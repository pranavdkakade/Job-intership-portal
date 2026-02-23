from django.urls import include, path
from .views import start_interview, interview_history

app_name = "interviews"

urlpatterns = [
    path('interview/', start_interview, name='start_interview'),
    path('history/', interview_history, name='interview_history'),
    path("interview-api/", include("interviews.api.urls_api")),
]
