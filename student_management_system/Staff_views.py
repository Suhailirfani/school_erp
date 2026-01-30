from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from hadiya.models import CustomUser, Staff, Course, Subject, Student, Attendance, Attendance_Report, Student_Result, Staff_leave, Staff_Feedback, Examination
from django.core import serializers
import json
import datetime

def staff_home(request):
    """Staff Dashboard view"""
    return render(request, 'Staff/home.html')

def take_attendance(request):
    """View to select Course/Session for taking attendance"""
    # Fetch all courses
    courses = Course.objects.all()
    context = {
        'courses': courses,
    }
    return render(request, 'Staff/take_attendance.html', context)

@csrf_exempt
def get_students(request):
    """AJAX view to get students based on course and session"""
    if request.method != "POST":
        return HttpResponse("Method Not Allowed")
        
    course_id = request.POST.get('course_id')
    
    try:
        course = Course.objects.get(id=course_id)
        
        # Get students in the course associated with the session year
        students = Student.objects.filter(course_id=course)
        
        list_data = []
        for student in students:
            data_small = {
                "id": student.admin.id, 
                "name": student.admin.first_name + " " + student.admin.last_name
            }
            list_data.append(data_small)
            
        return JsonResponse(json.dumps(list_data), content_type="application/json", safe=False)
    except Exception as e:
        return HttpResponse(str(e))

@csrf_exempt
def save_attendance_data(request):
    """AJAX view to save attendance data"""
    if request.method != "POST":
        return HttpResponse("Method Not Allowed")
        
    student_ids = request.POST.get("student_ids")
    course_id = request.POST.get("course_id")
    attendance_date = request.POST.get("attendance_date")
    
    try:
        course = Course.objects.get(id=course_id)
        
        # Check if attendance exists - Removed as per requirement
        # if Attendance.objects.filter(course=course, attendance_date=attendance_date, session_year_id=session_year).exists():
        #     return HttpResponse("Attendance already taken for this date. Please use Update Attendance.")
            
        # Save Attendance Record
        attendance = Attendance(
            course=course,
            attendance_date=attendance_date,
            # session_year_id=session_year
        )
        attendance.save()
        
        # Save Student Attendance Reports
        json_student_ids = json.loads(student_ids)
        for stud_dict in json_student_ids:
            student_id = stud_dict['id']
            status = stud_dict['status'] # 1 for Present, 0 for Absent
            leave_status = stud_dict.get('leave_status', '') # Informed/Not Informed/Empty
            
            student = Student.objects.get(admin_id=student_id)
            
            attendance_report = Attendance_Report(
                student=student,
                attendance=attendance,
                is_present=bool(status),
                leave_status=leave_status
            )
            attendance_report.save()
            
        return HttpResponse("OK")
    except Exception as e:
        return HttpResponse(f"Error: {str(e)}")

def update_attendance(request):
    """View to select date for updating attendance"""
    courses = Course.objects.all()
    context = {
        'courses': courses,
    }
    return render(request, 'Staff/update_attendance.html', context)

@csrf_exempt
def get_attendance_dates(request):
    """AJAX view to get dates with existing attendance records"""
    if request.method != "POST":
        return HttpResponse("Method Not Allowed")
    
    course_id = request.POST.get("course_id")
    try:
        course = Course.objects.get(id=course_id)
        
        attendance_objects = Attendance.objects.filter(course=course)
        
        list_data = []
        for attendance in attendance_objects:
            data_small = {
                "id": attendance.id,
                "attendance_date": str(attendance.attendance_date),
            }
            list_data.append(data_small)
            
        return JsonResponse(json.dumps(list_data), content_type="application/json", safe=False)
    except Exception as e:
        return HttpResponse(str(e))

@csrf_exempt
def get_attendance_student(request):
    """AJAX view to get student attendance data for update"""
    if request.method != "POST":
        return HttpResponse("Method Not Allowed")
        
    attendance_date = request.POST.get("attendance_date")
    attendance_id = request.POST.get("attendance_id")
    
    try:
        attendance = Attendance.objects.get(id=attendance_id)
        attendance_data = Attendance_Report.objects.filter(attendance=attendance)
        
        list_data = []
        for student_data in attendance_data:
            data_small = {
                "id": student_data.student.admin.id,
                "name": student_data.student.admin.first_name + " " + student_data.student.admin.last_name,
                "status": 1 if student_data.is_present else 0,
                "leave_status": student_data.leave_status if student_data.leave_status else ''
            }
            list_data.append(data_small)
            
        return JsonResponse(json.dumps(list_data), content_type="application/json", safe=False)
    except Exception as e:
        return HttpResponse(str(e))

@csrf_exempt
def save_updateattendance_data(request):
    """AJAX view to save updated attendance data"""
    if request.method != "POST":
        return HttpResponse("Method Not Allowed")
        
    student_ids = request.POST.get("student_ids")
    attendance_date = request.POST.get("attendance_date")
    attendance_id = request.POST.get("attendance_id")
    
    try:
        attendance = Attendance.objects.get(id=attendance_id)
        attendance.attendance_date = attendance_date
        attendance.save()
        
        json_student_ids = json.loads(student_ids)
        for stud_dict in json_student_ids:
            student_id = stud_dict['id']
            status = stud_dict['status']
            leave_status = stud_dict.get('leave_status', '')
            
            student = Student.objects.get(admin_id=student_id)
            
            attendance_report = Attendance_Report.objects.get(student=student, attendance=attendance)
            attendance_report.is_present = bool(status)
            attendance_report.leave_status = leave_status
            attendance_report.save()
            
        return HttpResponse("OK")
    except Exception as e:
        return HttpResponse(f"Error: {str(e)}")

def staff_add_result(request):
    """View to add/edit student results for staff subjects"""
    staff = Staff.objects.get(admin=request.user.id)
    subjects = Subject.objects.filter(staff=staff)
    exams = Examination.objects.all()
    context = {
        'subjects': subjects,
        'exams': exams
    }
    return render(request, 'Staff/add_result.html', context)


@csrf_exempt
def staff_get_students_for_result(request):
    """Fetch students and their existing marks for a subject (Staff)"""
    if request.method != "POST":
         return HttpResponse("Method Not Allowed")
         
    subject_id = request.POST.get("subject_id")
    exam_id = request.POST.get("exam_id")
    
    try:
        subject = Subject.objects.get(id=subject_id)
        # Students in the course of the subject
        students = Student.objects.filter(course_id=subject.course)
        
        if exam_id:
             exam = Examination.objects.get(id=exam_id)
        else:
             exam = None
        
        list_data = []
        for student in students:
            # Check if result already exists
            try:
                result = Student_Result.objects.get(student=student, subject=subject, exam=exam)
                ce_marks = result.ce_marks
                te_marks = result.te_marks
            except Student_Result.DoesNotExist:
                ce_marks = 0
                te_marks = 0
            
            data = {
                "id": student.admin.id, # Use User ID for identification
                "name": f"{student.admin.first_name} {student.admin.last_name}",
                "ce_marks": ce_marks,
                "te_marks": te_marks
            }
            list_data.append(data)
            
        return JsonResponse(json.dumps(list_data), content_type="application/json", safe=False)
    except Exception as e:
        return HttpResponse(str(e))


@csrf_exempt
def staff_save_student_result(request):
    """Save student marks (Staff)"""
    if request.method != "POST":
         return HttpResponse("Method Not Allowed")

    try:
        student_ids = request.POST.getlist("student_ids[]")
        ce_marks_list = request.POST.getlist("ce_marks[]")
        te_marks_list = request.POST.getlist("te_marks[]")
        subject_id = request.POST.get("subject_id")
        exam_id = request.POST.get("exam_id")
        
        subject = Subject.objects.get(id=subject_id)
        # Security check: Ensure staff owns this subject
        staff = Staff.objects.get(admin=request.user.id)
        if subject.staff != staff:
             return HttpResponse("Unauthorized Access to Subject")
             
        if exam_id:
             exam = Examination.objects.get(id=exam_id)
        else:
             exam = None

        for i in range(len(student_ids)):
            student_admin_id = student_ids[i]
            ce_marks = float(ce_marks_list[i])
            te_marks = float(te_marks_list[i])
            
            student = Student.objects.get(admin__id=student_admin_id)
            
            # Create or Update
            result, created = Student_Result.objects.update_or_create(
                student=student,
                subject=subject,
                exam=exam,
                defaults={
                    'ce_marks': ce_marks,
                    'te_marks': te_marks
                }
            )
            
        return HttpResponse("True")
    except Exception as e:
        return HttpResponse("False")


def staff_apply_leave(request):
    """View Pending Staff Leave Requests"""
    staff = Staff.objects.get(admin=request.user.id)
    leave_data = Staff_leave.objects.filter(staff=staff).order_by('-id')
    context = {
        'leave_data': leave_data
    }
    return render(request, 'Staff/apply_leave.html', context)


def staff_apply_leave_save(request):
    """Save Staff Leave"""
    if request.method != "POST":
        return redirect('staff_apply_leave')
    
    leave_date = request.POST.get('leave_date')
    leave_msg = request.POST.get('leave_msg')
    
    staff = Staff.objects.get(admin=request.user.id)
    
    leave_report = Staff_leave(
        staff=staff,
        leave_date=leave_date,
        leave_message=leave_msg,
        status=0
    )
    leave_report.save()
    messages.success(request, "Successfully Applied for Leave")
    return redirect('staff_apply_leave')


def staff_feedback(request):
    """View Staff Feedback and History"""
    staff = Staff.objects.get(admin=request.user.id)
    feedback_data = Staff_Feedback.objects.filter(staff=staff).order_by('-id')
    context = {
        'feedback_data': feedback_data
    }
    return render(request, 'Staff/feedback.html', context)


@csrf_exempt
def staff_feedback_save(request):
    """Save Staff Feedback"""
    if request.method != "POST":
        return redirect('staff_feedback')
        
    feedback = request.POST.get('feedback_msg')
    staff = Staff.objects.get(admin=request.user.id)
    
    try:
        feedback_obj = Staff_Feedback(staff=staff, feedback=feedback, feedback_reply="")
        feedback_obj.save()
        messages.success(request, "Feedback Sent Successfully")
    except Exception as e:
        messages.error(request, f"Failed to Send Feedback: {str(e)}")
        
    return redirect('staff_feedback')

def staff_view_attendance(request):
    """View to select criteria for viewing attendance (Staff)"""
    courses = Course.objects.all()
    students = Student.objects.select_related('admin').all()
    
    context = {
        'courses': courses,
        'students': students,
    }
    return render(request, 'Staff/view_attendance.html', context)

@csrf_exempt
def staff_get_attendance_data(request):
    """Get aggregated attendance report based on filters (Staff)"""
    if request.method != "POST":
        return HttpResponse("Method Not Allowed")
        
    course_id = request.POST.get("course_id")
    filter_type = request.POST.get("filter_type")
    start_date = request.POST.get("start_date")
    end_date = request.POST.get("end_date")
    month = request.POST.get("month")
    year = request.POST.get("year")
    
    try:
        if course_id:
            courses = Course.objects.filter(id=course_id)
        else:
            courses = Course.objects.all()
            
        final_data = []
        
        for course in courses:
            # Base query for Attendance
            attendance_query = Attendance.objects.filter(course=course)
            
            if filter_type == "day":
                attendance_query = attendance_query.filter(attendance_date=start_date)
            elif filter_type == "weekly":
                date_obj = datetime.datetime.strptime(start_date, "%Y-%m-%d").date()
                week_start = date_obj - datetime.timedelta(days=date_obj.weekday()) 
                week_end = week_start + datetime.timedelta(days=6)
                attendance_query = attendance_query.filter(attendance_date__range=[week_start, week_end])
            elif filter_type == "month":
                attendance_query = attendance_query.filter(attendance_date__month=month, attendance_date__year=year)
            elif filter_type == "year":
                attendance_query = attendance_query.filter(attendance_date__year=year)
            elif filter_type == "range":
                attendance_query = attendance_query.filter(attendance_date__range=[start_date, end_date])
            elif filter_type == "till_today":
                today = datetime.date.today()
                attendance_query = attendance_query.filter(attendance_date__lte=today)
                
            # LOGIC TO HANDLE DUPLICATES
            all_attendance = attendance_query.values('id', 'attendance_date', 'updated_at')
            
            latest_attendance_map = {}
            for att in all_attendance:
                d = str(att['attendance_date']) 
                if d not in latest_attendance_map:
                    latest_attendance_map[d] = att
                else:
                    if att['updated_at'] > latest_attendance_map[d]['updated_at']:
                        latest_attendance_map[d] = att
                        
            valid_attendance_ids = [item['id'] for item in latest_attendance_map.values()]
            total_days = len(valid_attendance_ids)
            
            students = Student.objects.filter(course_id=course)
            
            course_student_data = []
            if students.exists():
                for student in students:
                    present_count = Attendance_Report.objects.filter(
                        student=student, 
                        attendance__id__in=valid_attendance_ids, 
                        is_present=True
                    ).count()
                    
                    absent_count = Attendance_Report.objects.filter(
                        student=student, 
                        attendance__id__in=valid_attendance_ids, 
                        is_present=False
                    ).count()
                    
                    percentage = (present_count / total_days * 100) if total_days > 0 else 0
                    
                    data = {
                        "name": f"{student.admin.first_name} {student.admin.last_name}",
                        "total_days": total_days,
                        "present": present_count,
                        "absent": absent_count,
                        "percentage": round(percentage, 2)
                    }
                    course_student_data.append(data)
            
            final_data.append({
                "course_name": course.name,
                "data": course_student_data
            })
            
        return JsonResponse(json.dumps(final_data), content_type="application/json", safe=False)
    except Exception as e:
        return HttpResponse(str(e))

@csrf_exempt
def staff_get_student_attendance_data(request):
    """Get detailed attendance history for a single student (Staff)"""
    if request.method != "POST":
         return HttpResponse("Method Not Allowed")
         
    student_id = request.POST.get("student_id")
    start_date = request.POST.get("start_date")
    end_date = request.POST.get("end_date")
    
    try:
        student = Student.objects.get(admin__id=student_id)
        
        # Get all reports
        reports = Attendance_Report.objects.filter(student=student)
        
        if start_date and end_date:
            reports = reports.filter(attendance__attendance_date__range=[start_date, end_date])
            
        reports = reports.select_related('attendance').order_by('-attendance__attendance_date')
        
        all_reports = []
        for r in reports:
            all_reports.append({
                'date': str(r.attendance.attendance_date),
                'updated_at': r.attendance.updated_at, 
                'obj': r
            })
            
        all_reports.sort(key=lambda x: (x['date'], x['updated_at']), reverse=True)
        
        processed_dates = set()
        list_data = []
        for item in all_reports:
            date_str = item['date']
            if date_str not in processed_dates:
                processed_dates.add(date_str)
                report = item['obj']
                
                data = {
                    "date": date_str,
                    "status": "Present" if report.is_present else "Absent",
                    "leave_status": report.leave_status if report.leave_status else "-"
                }
                list_data.append(data)
            
        return JsonResponse(json.dumps(list_data), content_type="application/json", safe=False)
    except Exception as e:
        return HttpResponse(str(e))

@csrf_exempt
def staff_analyze_attendance(request):
    """Analyze attendance status (Staff)"""
    if request.method != "POST":
        return HttpResponse("Method Not Allowed")
        
    course_id = request.POST.get("course_id")
    analysis_type = request.POST.get("analysis_type") # below, above
    threshold = float(request.POST.get("threshold"))
    start_date = request.POST.get("start_date")
    end_date = request.POST.get("end_date")
    
    try:
        if course_id:
            courses = Course.objects.filter(id=course_id)
        else:
            courses = Course.objects.all()
            
        final_data = []
        
        for course in courses:
            students = Student.objects.filter(course_id=course)
            
            # Base Attendance Query
            attendance_query = Attendance.objects.filter(course=course)
            if start_date and end_date:
                attendance_query = attendance_query.filter(attendance_date__range=[start_date, end_date])
                
            # Handle Duplicates
            all_attendance = attendance_query.values('id', 'attendance_date', 'updated_at')
            latest_attendance_map = {}
            for att in all_attendance:
                d = str(att['attendance_date']) 
                if d not in latest_attendance_map:
                    latest_attendance_map[d] = att
                else:
                    if att['updated_at'] > latest_attendance_map[d]['updated_at']:
                        latest_attendance_map[d] = att
            valid_attendance_ids = [item['id'] for item in latest_attendance_map.values()]
            total_days = len(valid_attendance_ids)
            
            course_list_data = []
            if total_days > 0 and students.exists():
                for student in students:
                    present_count = Attendance_Report.objects.filter(
                        student=student, 
                        attendance__id__in=valid_attendance_ids, 
                        is_present=True
                    ).count()
                    
                    percentage = (present_count / total_days * 100)
                    percentage = round(percentage, 2)
                    
                    match = False
                    status = ""
                    
                    if analysis_type == 'below' and percentage < threshold:
                        match = True
                        status = "Low Attendance"
                    elif analysis_type == 'above' and percentage >= threshold:
                        match = True
                        status = "Good Standing"
                        
                    if match:
                        data = {
                            "name": f"{student.admin.first_name} {student.admin.last_name}",
                            "total_days": total_days,
                            "present": present_count,
                            "percentage": percentage,
                            "status": status
                        }
                        course_list_data.append(data)
                        
                if analysis_type == 'below':
                    course_list_data.sort(key=lambda x: x['percentage'])
                else:
                    course_list_data.sort(key=lambda x: x['percentage'], reverse=True)
                        
            final_data.append({
                "course_name": course.name,
                "data": course_list_data
            })
            
        return JsonResponse(json.dumps(final_data), content_type="application/json", safe=False)
    except Exception as e:
        return HttpResponse(str(e))

def staff_view_result(request):
    """View Results for Staff's subjects"""
    staff = Staff.objects.get(admin=request.user.id)
    subjects = Subject.objects.filter(staff=staff)
    exams = Examination.objects.all()
    context = {
        'subjects': subjects,
        'exams': exams
    }
    return render(request, 'Staff/view_result.html', context)

@csrf_exempt
def staff_get_result_data(request):
    """AJAX to fetch results for a staff's subject"""
    if request.method != "POST":
         return HttpResponse("Method Not Allowed")
    
    subject_id = request.POST.get("subject_id")
    exam_id = request.POST.get("exam_id")
    try:
        subject = Subject.objects.get(id=subject_id)
        # Verify subject belongs to staff (optional security check)
        # staff = Staff.objects.get(admin=request.user.id)
        # if subject.staff != staff: return HttpResponse("Unauthorized")
        
        if exam_id:
             exam = Examination.objects.get(id=exam_id)
        else:
             exam = None
             
        results = Student_Result.objects.filter(subject=subject, exam=exam)
        
        list_data = []
        for res in results:
            total = res.ce_marks + res.te_marks
            status = "Pass" if total >= 40 else "Fail" # Naive Pass Logic
            
            data = {
                "id": res.student.admin.id,
                "name": f"{res.student.admin.first_name} {res.student.admin.last_name}",
                "ce_marks": res.ce_marks,
                "te_marks": res.te_marks,
                "total": total,
                "result_status": status
            }
            list_data.append(data)
            
        return JsonResponse(json.dumps(list_data), content_type="application/json", safe=False)
    except Exception as e:
        return HttpResponse(str(e))

@csrf_exempt
def staff_analyze_result(request):
    """Analyze result for Staff subjects"""
    if request.method == "POST":
        action = request.POST.get("action")
        subject_id = request.POST.get("subject_id")
        exam_id = request.POST.get("exam_id")
        
        if action == 'fetch_graph':
            try:
                subject = Subject.objects.get(id=subject_id)
                
                if exam_id:
                     exam = Examination.objects.get(id=exam_id)
                     results = Student_Result.objects.filter(subject=subject, exam=exam)
                else:
                     results = Student_Result.objects.filter(subject=subject)
                
                grade_counts = {'A+':0, 'A':0, 'B+':0, 'B':0, 'C+':0, 'C':0, 'D':0}
                pass_count = 0
                fail_count = 0
                
                for res in results:
                    total = res.ce_marks + res.te_marks
                    sub_max = subject.max_ce_marks + subject.max_te_marks
                    perc = (total / sub_max * 100) if sub_max > 0 else 0
                    
                    if perc >= 40: pass_count += 1
                    else: fail_count += 1
                    
                    if perc >= 90: grade_counts['A+'] += 1
                    elif perc >= 80: grade_counts['A'] += 1
                    elif perc >= 70: grade_counts['B+'] += 1
                    elif perc >= 60: grade_counts['B'] += 1
                    elif perc >= 50: grade_counts['C+'] += 1
                    elif perc >= 40: grade_counts['C'] += 1
                    else: grade_counts['D'] += 1
                    
                data = {
                    "grade_labels": list(grade_counts.keys()),
                    "grade_counts": list(grade_counts.values()),
                    "pass_count": pass_count,
                    "fail_count": fail_count
                }
                return JsonResponse(json.dumps(data), content_type="application/json", safe=False)
            except Exception as e:
                return JsonResponse({'error': str(e)}, status=500)

    staff = Staff.objects.get(admin=request.user.id)
    subjects = Subject.objects.filter(staff=staff)
    exams = Examination.objects.all()
    context = {
        "subjects": subjects,
        "exams": exams
    }
    return render(request, "Staff/analyze_result.html", context)