from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import (
    CustomUser, Course, Staff, Subject, Student,
    Attendance, Attendance_Report, Student_Result, Student_Notification,
    Staff_Notification, Student_leave, Staff_leave, Student_Feedback,
    Staff_Feedback, Enquiry, News, BusStop
)


class CustomUserAdmin(UserAdmin):
    list_display = ('email', 'username', 'first_name', 'last_name', 'user_type', 'is_staff')
    list_filter = ('user_type', 'is_staff', 'is_active')
    search_fields = ('email', 'username', 'first_name', 'last_name')
    ordering = ('email',)
    
    fieldsets = UserAdmin.fieldsets + (
        ('Additional Info', {'fields': ('user_type', 'profile_pic')}),
    )
    add_fieldsets = UserAdmin.add_fieldsets + (
        ('Additional Info', {'fields': ('user_type', 'email', 'profile_pic')}),
    )


class CourseAdmin(admin.ModelAdmin):
    list_display = ('name', 'created_at', 'updated_at')
    search_fields = ('name',)


class SubjectAdmin(admin.ModelAdmin):
    list_display = ('name', 'course', 'staff', 'created_at')
    list_filter = ('course',)
    search_fields = ('name',)


class StudentAdmin(admin.ModelAdmin):
    list_display = ('get_full_name', 'course_id', 'admission_type', 'created_at')
    list_filter = ('course_id', 'admission_type', 'gender')
    search_fields = ('admin__first_name', 'admin__last_name', 'admin__email')
    
    def get_full_name(self, obj):
        return f"{obj.admin.first_name} {obj.admin.last_name}"
    get_full_name.short_description = 'Student Name'


class StaffAdmin(admin.ModelAdmin):
    list_display = ('get_full_name', 'gender', 'created_at')
    list_filter = ('gender',)
    search_fields = ('admin__first_name', 'admin__last_name', 'admin__email')
    
    def get_full_name(self, obj):
        return f"{obj.admin.first_name} {obj.admin.last_name}"
    get_full_name.short_description = 'Staff Name'


class AttendanceAdmin(admin.ModelAdmin):
    list_display = ('course', 'attendance_date')
    list_filter = ('course', 'attendance_date')


class AttendanceReportAdmin(admin.ModelAdmin):
    list_display = ('student', 'attendance', 'is_present', 'created_at')
    list_filter = ('is_present', 'attendance__attendance_date')
    search_fields = ('student__admin__first_name', 'student__admin__last_name')


class StudentResultAdmin(admin.ModelAdmin):
    list_display = ('student', 'subject', 'ce_marks', 'te_marks', 'get_total')
    list_filter = ('subject__course',)
    search_fields = ('student__admin__first_name', 'student__admin__last_name')
    
    def get_total(self, obj):
        return obj.total_marks()
    get_total.short_description = 'Total Marks'


class EnquiryAdmin(admin.ModelAdmin):
    list_display = ('name', 'phone_number', 'course', 'percentage', 'token', 'created_at')
    list_filter = ('course', 'district')
    search_fields = ('name', 'phone_number', 'token')


class NewsAdmin(admin.ModelAdmin):
    list_display = ('title', 'created_at')
    search_fields = ('title', 'content')


# Register models
admin.site.register(CustomUser, CustomUserAdmin)
admin.site.register(Course, CourseAdmin)

admin.site.register(Staff, StaffAdmin)
admin.site.register(Subject, SubjectAdmin)
admin.site.register(Student, StudentAdmin)
admin.site.register(BusStop)
admin.site.register(Attendance, AttendanceAdmin)
admin.site.register(Attendance_Report, AttendanceReportAdmin)
admin.site.register(Student_Result, StudentResultAdmin)
admin.site.register(Student_Notification)
admin.site.register(Staff_Notification)
admin.site.register(Student_leave)
admin.site.register(Staff_leave)
admin.site.register(Student_Feedback)
admin.site.register(Staff_Feedback)
admin.site.register(Enquiry, EnquiryAdmin)
admin.site.register(News, NewsAdmin)
