from django.urls import path
from .views_applied import applied_companies
from .views_applied import apply_companies

urlpatterns = [
    path('applied/', applied_companies, name='applied_companies'),
    path('apply/', apply_companies, name='apply_companies'),
]
