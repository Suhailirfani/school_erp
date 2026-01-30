from django.urls import path
from student_management_system import Management_views

urlpatterns = [
    path('', Management_views.management_dashboard, name='management_dashboard'),
]
