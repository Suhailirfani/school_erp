from django.urls import path
from student_management_system import Staff_views

urlpatterns = [
    path('', Staff_views.staff_home, name='staff_home'),
    path('take_attendance/', Staff_views.take_attendance, name='take_attendance'),
    path('save_attendance_data/', Staff_views.save_attendance_data, name='save_attendance_data'),
    path('update_attendance/', Staff_views.update_attendance, name='update_attendance'),
    path('save_updateattendance_data/', Staff_views.save_updateattendance_data, name='save_updateattendance_data'),
    path('view_attendance/', Staff_views.staff_view_attendance, name='staff_view_attendance'),
    path('get_attendance_data/', Staff_views.staff_get_attendance_data, name='staff_get_attendance_data'),
    path('get_student_attendance_data/', Staff_views.staff_get_student_attendance_data, name='staff_get_student_attendance_data'),
    path('analyze_attendance/', Staff_views.staff_analyze_attendance, name='staff_analyze_attendance'),
    
    # AJAX Views
    path('get_students/', Staff_views.get_students, name='get_students'),
    path('get_attendance_dates/', Staff_views.get_attendance_dates, name='get_attendance_dates'),
    path('get_attendance_student/', Staff_views.get_attendance_student, name='get_attendance_student'),
    
    # Result Management
    path('results/add/', Staff_views.staff_add_result, name='staff_add_result'),
    path('results/view/', Staff_views.staff_view_result, name='staff_view_result'),
    path('get_result_data/', Staff_views.staff_get_result_data, name='staff_get_result_data'),
    path('results/analyze/', Staff_views.staff_analyze_result, name='staff_analyze_result'),
    path('get_students_for_result/', Staff_views.staff_get_students_for_result, name='staff_get_students_for_result'),
    path('save_student_result/', Staff_views.staff_save_student_result, name='staff_save_student_result'),
    
    # Leave Management
    path('apply_leave/', Staff_views.staff_apply_leave, name='staff_apply_leave'),
    path('apply_leave_save/', Staff_views.staff_apply_leave_save, name='staff_apply_leave_save'),
    
    # Feedback
    path('feedback/', Staff_views.staff_feedback, name='staff_feedback'),
    path('feedback/save/', Staff_views.staff_feedback_save, name='staff_feedback_save'),
]
