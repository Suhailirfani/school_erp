from django.urls import path
from student_management_system import Hod_views

urlpatterns = [
    # Dashboard
    path('', Hod_views.dashboard, name='hod_dashboard'),
    
    # Student Management
    path('students/', Hod_views.view_students, name='view_students'),
    path('students/add/', Hod_views.add_student, name='add_student'),
    path('students/edit/<int:student_id>/', Hod_views.edit_student, name='edit_student'),
    path('students/delete/<int:student_id>/', Hod_views.delete_student, name='delete_student'),

    # Staff Management
    path('staff/', Hod_views.view_staff, name='view_staff'),
    path('staff/add/', Hod_views.add_staff, name='add_staff'),
    path('staff/edit/<int:staff_id>/', Hod_views.edit_staff, name='edit_staff'),
    path('staff/delete/<int:staff_id>/', Hod_views.delete_staff, name='delete_staff'),

    # Course Management
    path('courses/', Hod_views.view_courses, name='view_courses'),
    path('courses/add/', Hod_views.add_course, name='add_course'),
    path('courses/edit/<int:course_id>/', Hod_views.edit_course, name='edit_course'),
    path('courses/delete/<int:course_id>/', Hod_views.delete_course, name='delete_course'),

    # Subject Management
    path('subjects/', Hod_views.view_subjects, name='view_subjects'),
    path('subjects/add/', Hod_views.add_subject, name='add_subject'),
    path('subjects/edit/<int:subject_id>/', Hod_views.edit_subject, name='edit_subject'),
    path('subjects/edit/<int:subject_id>/', Hod_views.edit_subject, name='edit_subject'),
    path('subjects/delete/<int:subject_id>/', Hod_views.delete_subject, name='delete_subject'),
    path('subject_type/manage/', Hod_views.manage_subject_type, name='manage_subject_type'),
    path('subject_type/add/', Hod_views.add_subject_type, name='add_subject_type'),
    path('subject_type/delete/<int:type_id>/', Hod_views.delete_subject_type, name='delete_subject_type'),

    # Session Management - Removed
    # path('sessions/', Hod_views.view_sessions, name='view_sessions'),
    # path('sessions/add/', Hod_views.add_session, name='add_session'),
    # path('sessions/edit/<int:session_id>/', Hod_views.edit_session, name='edit_session'),
    # path('sessions/delete/<int:session_id>/', Hod_views.delete_session, name='delete_session'),

    # Attendance Management
    path('take_attendance/', Hod_views.admin_take_attendance, name='admin_take_attendance'),
    path('get_students_attendance/', Hod_views.admin_get_students_attendance, name='admin_get_students_attendance'),
    path('save_attendance_data/', Hod_views.admin_save_attendance_data, name='admin_save_attendance_data'),
    path('update_attendance/', Hod_views.admin_update_attendance, name='admin_update_attendance'),
    path('save_updateattendance_data/', Hod_views.admin_save_updateattendance_data, name='admin_save_updateattendance_data'),
    path('admin_view_attendance/', Hod_views.admin_view_attendance, name='admin_view_attendance'),
    path('admin_get_attendance_dates/', Hod_views.admin_get_attendance_dates, name='admin_get_attendance_dates'),
    path('admin_get_attendance_student/', Hod_views.admin_get_attendance_student, name='admin_get_attendance_student'),
    path('admin_get_attendance_report_data/', Hod_views.admin_get_attendance_report_data, name='admin_get_attendance_report_data'),
    path('admin_get_student_attendance_data/', Hod_views.admin_get_student_attendance_data, name='admin_get_student_attendance_data'),
    path('admin_analyze_attendance/', Hod_views.admin_analyze_attendance, name='admin_analyze_attendance'),
    path('download_sample_file/<str:file_type>/', Hod_views.download_sample_file, name='download_sample_file'),
    
    # Result Management
    path('results/add/', Hod_views.add_result, name='add_result'),
    path('results/view/', Hod_views.admin_view_result, name='admin_view_result'),
    path('results/manage_exam/', Hod_views.manage_exam, name='manage_exam'),
    path('results/add_exam/', Hod_views.add_exam, name='add_exam'),
    path('results/delete_exam/<int:exam_id>/', Hod_views.delete_exam, name='delete_exam'),
    path('manage_subject_type/', Hod_views.manage_subject_type, name="manage_subject_type"),
    path('add_subject_type/', Hod_views.add_subject_type, name="add_subject_type"),
    path('edit_subject_type/<int:subject_type_id>/', Hod_views.edit_subject_type, name="edit_subject_type"),
    path('delete_subject_type/<int:subject_type_id>/', Hod_views.delete_subject_type, name="delete_subject_type"),
    path('admin_get_subjects/', Hod_views.admin_get_subjects, name='admin_get_subjects'),
    path('admin_get_students/', Hod_views.admin_get_students, name='admin_get_students'),
    path('admin_get_students_for_result/', Hod_views.admin_get_students_for_result, name='admin_get_students_for_result'),
    path('admin_save_student_result/', Hod_views.admin_save_student_result, name='admin_save_student_result'),
    path('admin_get_result_data/', Hod_views.admin_get_result_data, name='admin_get_result_data'),
    path('generate_result_pdf/', Hod_views.generate_result_pdf, name='generate_result_pdf'),
    path('results/analyze/', Hod_views.admin_analyze_result, name='admin_analyze_result'),
    
    # Leave Management
    path('student/leave/', Hod_views.admin_view_student_leave, name='admin_view_student_leave'),
    path('student/leave/approve/<int:leave_id>/', Hod_views.admin_approve_student_leave, name='admin_approve_student_leave'),
    path('student/leave/disapprove/<int:leave_id>/', Hod_views.admin_disapprove_student_leave, name='admin_disapprove_student_leave'),
    path('staff/leave/', Hod_views.admin_view_staff_leave, name='admin_view_staff_leave'),
    path('staff/leave/approve/<int:leave_id>/', Hod_views.admin_approve_staff_leave, name='admin_approve_staff_leave'),
    path('staff/leave/disapprove/<int:leave_id>/', Hod_views.admin_disapprove_staff_leave, name='admin_disapprove_staff_leave'),
    
    # Feedback Management
    path('student/feedback/', Hod_views.admin_view_student_feedback, name='admin_view_student_feedback'),
    path('student/feedback/reply/', Hod_views.admin_reply_student_feedback, name='admin_reply_student_feedback'),
    path('staff/feedback/', Hod_views.admin_view_staff_feedback, name='admin_view_staff_feedback'),
    path('staff/feedback/reply/', Hod_views.admin_reply_staff_feedback, name='admin_reply_staff_feedback'),
]
