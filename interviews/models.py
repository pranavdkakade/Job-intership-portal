from django.db import models
from django.contrib.auth.models import User


class InterviewSession(models.Model):
    STAGE_CHOICES = [
        ("waiting_for_start", "Waiting For Start"),
        ("waiting_for_role", "Waiting For Role"),
        ("waiting_for_topics", "Waiting For Topics"),
        ("interview_started", "Interview Started"),
        ("waiting_for_answer", "Waiting For Answer"),
        ("completed", "Completed"),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    role = models.CharField(max_length=100, null=True, blank=True)
    topics = models.TextField(null=True, blank=True)

    current_question_number = models.IntegerField(default=0)
    total_score = models.FloatField(default=0)

    stage = models.CharField(
        max_length=50,
        choices=STAGE_CHOICES,
        default="waiting_for_start"
    )

    is_completed = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)


class InterviewQuestion(models.Model):
    session = models.ForeignKey(
        InterviewSession,
        on_delete=models.CASCADE,
        related_name="questions"
    )

    question_text = models.TextField()
    user_answer = models.TextField(null=True, blank=True)
    score = models.FloatField(null=True, blank=True)
    feedback = models.TextField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
