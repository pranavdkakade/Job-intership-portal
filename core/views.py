from django.shortcuts import render, redirect

def home(request):
    # If user is logged in, redirect to dashboard
    if request.user.is_authenticated:
        return redirect('users:user_dashboard')
    return render(request, "core/home.html")

def jobs(request):
    return render(request, "core/jobs.html")