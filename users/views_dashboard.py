from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from interviews.models import CVInterviewSession, InterviewSession
from django.db.models import Avg, Count

@login_required(login_url='users:auth')
def dashboard(request):
    """User Dashboard with CV Interview Results and Single Topic Proficiency"""
    # Fetch completed CV interview sessions for the logged-in user
    cv_sessions = CVInterviewSession.objects.filter(
        user=request.user,
        is_completed=True
    ).select_related('resume').order_by('created_at')
    
    # Prepare data for CV interview graph
    resume_labels = []
    resume_scores = []
    
    for index, session in enumerate(cv_sessions, start=1):
        resume_labels.append(f"Resume {index}")
        resume_scores.append(session.get_score_percentage())
    
    # Single Topic Proficiency Statistics (SQL and Python)
    single_topic_sessions = InterviewSession.objects.filter(
        user=request.user,
        mode='single',
        is_completed=True
    )
    
    # Calculate SQL statistics
    sql_sessions = single_topic_sessions.filter(topics__iexact='sql')
    sql_count = sql_sessions.count()
    sql_avg = sql_sessions.aggregate(Avg('percentage_score'))['percentage_score__avg'] or 0
    
    # Calculate Python statistics
    python_sessions = single_topic_sessions.filter(topics__iexact='python')
    python_count = python_sessions.count()
    python_avg = python_sessions.aggregate(Avg('percentage_score'))['percentage_score__avg'] or 0
    
    context = {
        'resume_labels': resume_labels,
        'resume_scores': resume_scores,
        'total_interviews': cv_sessions.count(),
        # Single Topic Proficiency Data
        'sql_avg_score': round(sql_avg, 1) if sql_avg else 0,
        'sql_interview_count': sql_count,
        'python_avg_score': round(python_avg, 1) if python_avg else 0,
        'python_interview_count': python_count,
    }
    
    return render(request, 'users/dashboard/dashboard.html', context)
