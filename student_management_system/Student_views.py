from django.shortcuts import render, redirect
from django.contrib import messages
from hadiya.models import CustomUser, Student, Course, Subject, Attendance, Attendance_Report, Student_Feedback, Student_leave, Student_Result
from django.contrib.auth.decorators import login_required
from student_management_system.Hod_views import render_to_pdf
import datetime
import json

def student_home(request):
    """Student Dashboard"""
    student_obj = Student.objects.get(admin=request.user.id)
    attendance_total = Attendance_Report.objects.filter(student=student_obj).count()
    attendance_present = Attendance_Report.objects.filter(student=student_obj, is_present=True).count()
    attendance_absent = Attendance_Report.objects.filter(student=student_obj, is_present=False).count()
    
    course = student_obj.course_id # Corrected field name from course to course_id based on models.py
    subjects = Subject.objects.filter(course=course).count()
    
    subject_name = []
    data_present = []
    data_absent = []
    subject_data = Subject.objects.filter(course=course)
    
    for subject in subject_data:
        attendance = Attendance.objects.filter(course=course)
        attendance_present_count = Attendance_Report.objects.filter(attendance__in=attendance, is_present=True, student=student_obj, attendance__course=course).count()
        # Logic for subject wise attendance is limited by model design, as discussed.
        pass

    context={
        "attendance_total": attendance_total,
        "attendance_present": attendance_present,
        "attendance_absent": attendance_absent,
        "subjects": subjects,
        "subject_name": subject_name,
        "data_present": data_present,
        "data_absent": data_absent
    }
    return render(request, "Student/home.html", context)

def student_view_attendance(request):
    """View Attendance History"""
    student = Student.objects.get(admin=request.user.id)
    course = student.course_id
    subjects = Subject.objects.filter(course=course)
    
    context = {
        "subjects": subjects
    }
    return render(request, "Student/view_attendance.html", context)

def student_view_attendance_post(request):
    """Handle attendance view filters"""
    if request.method != "POST":
         return redirect('student_view_attendance')
         
    subject_id = request.POST.get('subject') # Optional filtering by subject if needed later
    filter_type = request.POST.get('filter_type')
    start_date = request.POST.get('start_date')
    end_date = request.POST.get('end_date')
    date_val = request.POST.get('date_val') # For daily/weekly
    month = request.POST.get('month')
    year = request.POST.get('year')

    student = Student.objects.get(admin=request.user.id)
    subjects = Subject.objects.filter(course=student.course_id)
    subject = None
    if subject_id:
        subject = Subject.objects.get(id=subject_id)
    
    attendance = Attendance.objects.filter(course=student.course_id)
    
    if filter_type == "day":
        attendance = attendance.filter(attendance_date=date_val)
    elif filter_type == "weekly":
         # Weekly logic
        date_obj = datetime.datetime.strptime(date_val, "%Y-%m-%d").date()
        week_start = date_obj - datetime.timedelta(days=date_obj.weekday())
        week_end = week_start + datetime.timedelta(days=6)
        attendance = attendance.filter(attendance_date__range=[week_start, week_end])
    elif filter_type == "month":
        attendance = attendance.filter(attendance_date__month=month, attendance_date__year=year)
    elif filter_type == "year":
        attendance = attendance.filter(attendance_date__year=year)
    elif filter_type == "range":
        attendance = attendance.filter(attendance_date__range=(start_date, end_date))
    elif filter_type == "till_today":
        today = datetime.date.today()
        attendance = attendance.filter(attendance_date__lte=today)

    attendance_reports = Attendance_Report.objects.filter(attendance__in=attendance, student=student)
    
    context = {
        "attendance_reports": attendance_reports,
        "subject": subject,
        "subjects": Subject.objects.filter(course=student.course_id)
    }
    return render(request, "Student/view_attendance.html", context)


def student_apply_leave(request):
    """Apply for Leave"""
    student = Student.objects.get(admin=request.user.id)
    leave_data = Student_leave.objects.filter(student=student).order_by('-id')
    context = {
        "leave_data": leave_data
    }
    return render(request, 'Student/apply_leave.html', context)

def student_apply_leave_save(request):
    """Save Leave Application"""
    if request.method != "POST":
        return redirect('student_apply_leave')
    
    leave_date = request.POST.get('leave_date')
    leave_msg = request.POST.get('leave_msg')
    
    student = Student.objects.get(admin=request.user.id)
    
    leave_report = Student_leave(student=student, leave_date=leave_date, leave_message=leave_msg, status=0)
    leave_report.save()
    messages.success(request, "Successfully Applied for Leave")
    return redirect('student_apply_leave')

def student_feedback(request):
    """Send Feedback"""
    student = Student.objects.get(admin=request.user.id)
    feedback_data = Student_Feedback.objects.filter(student=student).order_by('-id')
    context = {
        "feedback_data": feedback_data
    }
    return render(request, 'Student/feedback.html', context)

def student_feedback_save(request):
    """Save Feedback"""
    if request.method != "POST":
        return redirect('student_feedback')
    
    feedback_msg = request.POST.get('feedback_msg')
    
    student = Student.objects.get(admin=request.user.id)
    feedback = Student_Feedback(student=student, feedback=feedback_msg, feedback_reply="")
    feedback.save()
    messages.success(request, "Feedback Sent Successfully")
    return redirect('student_feedback')


def student_view_result(request):
    """View Student Results"""
    student = Student.objects.get(admin=request.user.id)
    student_result = Student_Result.objects.filter(student=student)
    
    # Calculate Totals and Grading
    processed_results = []
    total_obtained = 0
    total_max = 0
    
    for result in student_result:
        ce = result.ce_marks
        te = result.te_marks
        total = ce + te
        sub_max = result.subject.max_ce_marks + result.subject.max_te_marks
        
        total_obtained += total
        total_max += sub_max
        
        perc = (total / sub_max * 100) if sub_max > 0 else 0
        grade = ''
        if perc >= 90: grade = 'A+'
        elif perc >= 80: grade = 'A'
        elif perc >= 70: grade = 'B+'
        elif perc >= 60: grade = 'B'
        elif perc >= 50: grade = 'C+'
        elif perc >= 40: grade = 'C'
        else: grade = 'D'

        processed_results.append({
            'subject': result.subject,
            'ce_marks': ce,
            'te_marks': te,
            'total_marks': total,
            'max_total': sub_max,
            'grade': grade
        })
        
    overall_percentage = (total_obtained / total_max * 100) if total_max > 0 else 0
    
    context = {
        "student_result": processed_results,
        "total_obtained": total_obtained, 
        "total_max": total_max,
        "overall_percentage": overall_percentage
    }
    return render(request, "Student/view_result.html", context)


def student_download_result_pdf(request):
    """Download Student Progress Card PDF"""
    student = Student.objects.get(admin=request.user.id)
    student_result = Student_Result.objects.filter(student=student)
    course = student.course_id
    subjects = Subject.objects.filter(course=course)
    
    context = {
        'view_type': 'student_wise',
        'student': student,
        'course': course
    }
    
    total_obtained = 0
    total_max = 0
    data = []
    
    for subject in subjects:
        try:
            result = Student_Result.objects.get(student=student, subject=subject)
            ce = result.ce_marks
            te = result.te_marks
            total = ce + te
        except Student_Result.DoesNotExist:
            ce = 0
            te = 0
            total = 0
        
        sub_max = subject.max_ce_marks + subject.max_te_marks
        total_obtained += total
        total_max += sub_max
        
        perc = (total / sub_max * 100) if sub_max > 0 else 0
        
        data.append({
            "subject_name": subject.name,
            "max_ce_marks": subject.max_ce_marks,
            "max_te_marks": subject.max_te_marks,
            "ce_marks": ce,
            "te_marks": te,
            "total_marks": total,
            "percentage": perc
        })
    
    context['data'] = data
    context['total_max'] = total_max
    context['overall_percentage'] = (total_obtained / total_max * 100) if total_max > 0 else 0
            
    return render_to_pdf('Hod/result_pdf_template.html', context)
    
    
# --- Fee Management (Student Side) ---

def student_view_fees(request):
    """View My Fees and Payments"""
    from hadiya.models import StudentInvoice, FeePayment
    
    student = Student.objects.get(admin=request.user.id)
    invoices = StudentInvoice.objects.filter(student=student).order_by('-created_at')
    payments = FeePayment.objects.filter(student=student).order_by('-created_at')
    
    context = {
        'student': student,
        'invoices': invoices,
        'payments': payments
    }
    return render(request, 'Student/view_fees.html', context)
    
def student_download_receipt(request, payment_id):
    """Download Payment Receipt (PDF or Print View)"""
    # Reuse Accountant Print View for convenience or create PDF
    from hadiya.models import FeePayment
    
    payment = FeePayment.objects.get(id=payment_id)
    # Ensure this payment belongs to the logged-in student for security !
    if payment.student.admin.id != request.user.id:
        messages.error(request, "Access Denied")
        return redirect('student_view_fees')
        
    allocations = payment.allocations.all()
    # Using the same template as Accountant
    return render(request, 'Accountant/print_invoice.html', {
        'payment': payment,
        'allocations': allocations
    })