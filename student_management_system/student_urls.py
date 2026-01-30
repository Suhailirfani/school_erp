from django.urls import path
from student_management_system import Student_views

urlpatterns = [
    path('', Student_views.student_home, name='student_home'),
    path('view_attendance/', Student_views.student_view_attendance, name='student_view_attendance'),
    path('view_attendance_post/', Student_views.student_view_attendance_post, name='student_view_attendance_post'),
    path('view_result/', Student_views.student_view_result, name='student_view_result'),
    path('apply_leave/', Student_views.student_apply_leave, name='student_apply_leave'),
    path('apply_leave_save/', Student_views.student_apply_leave_save, name='student_apply_leave_save'),
    path('feedback/', Student_views.student_feedback, name='student_feedback'),
    path('feedback_save/', Student_views.student_feedback_save, name='student_feedback_save'),
    path('download_result_pdf/', Student_views.student_download_result_pdf, name='student_download_result_pdf'),
    path('view_fees/', Student_views.student_view_fees, name='student_view_fees'),
    path('download_receipt/<int:payment_id>/', Student_views.student_download_receipt, name='student_download_receipt'),
]
