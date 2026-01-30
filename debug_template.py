import os
import django
import sys
from django.template import Template, Context
from django.template.loader import get_template

sys.path.append('d:\\work\\school_erp')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'student_management_system.settings')
django.setup()

from hadiya.models import Student, Course

print("Rendering Hod/home.html...")

try:
    # Fetch a student for context
    student = Student.objects.first()
    if not student:
        print("No students found to test with.")
    else:
        print(f"Testing with student: {student.admin.first_name}, Course: {student.course_id.name}")
        
    # Mock context based on the view
    context_data = {
        'students_count': 10,
        'staff_count': 5,
        'courses_count': 3,
        'subjects_count': 20,
        'recent_students': [student] if student else [],
        'recent_enquiries': [],
        'recent_news': [],
        'pending_student_leaves': 0,
        'pending_staff_leaves': 0,
        'unread_student_feedbacks': 0,
        'unread_staff_feedbacks': 0,
    }
    
    # Render template
    t = get_template('Hod/home.html')
    rendered = t.render(context_data)
    
    with open('debug_output.txt', 'w', encoding='utf-8') as f:
        f.write(f"Student used for test: {student.admin.first_name} {student.admin.last_name}\n")
        f.write(f"Course Name in Python: '{student.course_id.name}'\n")
        
        # Check for the problematic string
        if "{{ STUDENT.COURSE_ID.NAME }}" in rendered:
            f.write("\nFOUND THE LITERAL STRING IN OUTPUT!\n")
        elif "{{ student.course_id.name }}" in rendered:
             f.write("\nFOUND LOWERCASE LITERAL STRING IN OUTPUT!\n")
        else:
            f.write("\nLiteral string NOT found. Searching for course name...\n")
            if student and student.course_id.name in rendered:
                f.write(f"Found course name '{student.course_id.name}' in output. Rendering CORRECT.\n")
            else:
                f.write("Course name NOT found in output.\n")
                
        # Find the specific student row in rendered HTML
        name_str = f"{student.admin.first_name} {student.admin.last_name}"
        start_idx = rendered.find(name_str)
        if start_idx != -1:
            f.write("\nSnippet around 'Recent Students' row:\n")
            # Print 500 chars after the name
            f.write(rendered[start_idx:start_idx+500])
        else:
            f.write(f"\nCould not find student name '{name_str}' in rendered output.\n")

except Exception as e:
    with open('debug_output.txt', 'w') as f:
        f.write(f"Error: {e}")
