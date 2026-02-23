from django.urls import path
from .views_api import chat_interview

urlpatterns = [
    path("chat/", chat_interview, name="chat_interview"),
]