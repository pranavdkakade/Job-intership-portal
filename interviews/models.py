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

    DIFFICULTY_CHOICES = [
        ("beginner", "Beginner"),
        ("intermediate", "Intermediate"),
        ("advanced", "Advanced"),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    role = models.CharField(max_length=100, null=True, blank=True)
    topics = models.TextField(null=True, blank=True)
    difficulty_level = models.CharField(max_length=20, choices=DIFFICULTY_CHOICES, default="intermediate")

    current_question_number = models.IntegerField(default=0)
    total_questions = models.IntegerField(default=5)
    total_score = models.FloatField(default=0)
    max_score = models.FloatField(default=100)
    percentage_score = models.FloatField(default=0)

    stage = models.CharField(
        max_length=50,
        choices=STAGE_CHOICES,
        default="waiting_for_start"
    )

    is_completed = models.BooleanField(default=False)
    duration_minutes = models.IntegerField(default=0)  # Interview duration
    created_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.user.username} - {self.role} ({self.created_at.strftime('%Y-%m-%d')})"

    def get_score_percentage(self):
        if self.max_score > 0:
            return round((self.total_score / self.max_score) * 100, 1)
        return 0

    def get_performance_grade(self):
        percentage = self.get_score_percentage()
        if percentage >= 90:
            return "Excellent"
        elif percentage >= 80:
            return "Good"
        elif percentage >= 70:
            return "Average"
        elif percentage >= 60:
            return "Below Average"
        else:
            return "Needs Improvement"


class InterviewQuestion(models.Model):
    QUESTION_TYPES = [
        ("technical", "Technical"),
        ("behavioral", "Behavioral"),
        ("situational", "Situational"),
        ("coding", "Coding"),
    ]

    session = models.ForeignKey(
        InterviewSession,
        on_delete=models.CASCADE,
        related_name="questions"
    )

    question_number = models.IntegerField(default=1)
    question_type = models.CharField(max_length=20, choices=QUESTION_TYPES, default="technical")
    question_text = models.TextField()
    user_answer = models.TextField(null=True, blank=True)
    score = models.FloatField(null=True, blank=True, default=0)
    max_score = models.FloatField(default=20)  # Each question out of 20
    feedback = models.TextField(null=True, blank=True)
    ai_evaluation = models.JSONField(null=True, blank=True)  # Store AI evaluation details

    created_at = models.DateTimeField(auto_now_add=True)
    answered_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ['question_number']

    def __str__(self):
        return f"Q{self.question_number}: {self.question_text[:50]}..."

    def get_score_percentage(self):
        if self.max_score > 0:
            return round((self.score / self.max_score) * 100, 1)
        return 0
