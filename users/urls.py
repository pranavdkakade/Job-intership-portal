from django.urls import path
from django.contrib.auth.views import LogoutView
from . import views
from .views_dashboard import dashboard

app_name = "users"

urlpatterns = [
    # path("register/", views.register, name="register"),
    # path("login/", views.login_view, name="login"),
    path("auth/", views.auth_view, name="auth"),
    path("logout/", LogoutView.as_view(next_page='core:home'), name="logout"),
    path('dashboard/', dashboard, name='user_dashboard'),
]