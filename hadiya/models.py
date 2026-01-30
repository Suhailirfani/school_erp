from django.contrib.auth.models import AbstractUser
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
import datetime


class CustomUser(AbstractUser):
    USER_TYPE_CHOICES = (
        (1, 'HOD'),
        (2, 'Staff'),
        (3, 'Student'),
        (4, 'Accountant'),
        (5, 'Management'),
    )
    
    user_type = models.IntegerField(choices=USER_TYPE_CHOICES, default=1)
    profile_pic = models.ImageField(upload_to='profile_pics/', blank=True, null=True)
    email = models.EmailField(unique=True)
    
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username', 'first_name', 'last_name']
    
    def __str__(self):
        return f"{self.email} ({self.get_user_type_display()})"


class Course(models.Model):
    name = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return self.name


class Staff(models.Model):
    admin = models.OneToOneField(CustomUser, on_delete=models.CASCADE)
    address = models.TextField()
    gender = models.CharField(max_length=10, choices=[('Male', 'Male'), ('Female', 'Female'), ('Other', 'Other')])
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.admin.first_name} {self.admin.last_name}"


class Accountant(models.Model):
    admin = models.OneToOneField(CustomUser, on_delete=models.CASCADE)
    address = models.TextField()
    gender = models.CharField(max_length=10, choices=[('Male', 'Male'), ('Female', 'Female'), ('Other', 'Other')])
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.admin.first_name} {self.admin.last_name}"


class Management(models.Model):
    admin = models.OneToOneField(CustomUser, on_delete=models.CASCADE)
    address = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.admin.first_name} {self.admin.last_name}"


class SubjectType(models.Model):
    name = models.CharField(max_length=50)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name


class Examination(models.Model):
    name = models.CharField(max_length=50)
    date = models.DateField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name


class Subject(models.Model):
    name = models.CharField(max_length=100)
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='subjects')
    staff = models.ForeignKey(Staff, on_delete=models.SET_NULL, null=True, blank=True, related_name='subjects')
    subject_type = models.ForeignKey(SubjectType, on_delete=models.SET_NULL, null=True, blank=True)
    max_te_marks = models.FloatField(default=100.0, help_text='Maximum Term End marks')
    max_ce_marks = models.FloatField(default=100.0, help_text='Maximum Continuous Evaluation marks')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.name} ({self.course.name})"


class BusStop(models.Model):
    name = models.CharField(max_length=100)
    route = models.CharField(max_length=100, blank=True)
    monthly_fee = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    
    def __str__(self):
        return self.name


class Student(models.Model):
    ADMISSION_TYPE_CHOICES = (
        ('Day Scholar', 'Day Scholar'),
        ('Hostel', 'Hostel'),
    )
    
    admin = models.OneToOneField(CustomUser, on_delete=models.CASCADE)
    address = models.TextField()
    gender = models.CharField(max_length=10, choices=[('Male', 'Male'), ('Female', 'Female'), ('Other', 'Other')])
    course_id = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='students')
    # session_year_id = models.ForeignKey(Session_year, on_delete=models.CASCADE)
    admission_type = models.CharField(max_length=20, choices=ADMISSION_TYPE_CHOICES, default='Day Scholar')
    uses_hostel = models.BooleanField(default=False)
    
    uses_transport = models.BooleanField(default=False)
    transport_mode = models.CharField(max_length=20, choices=[('Bus', 'Bus'), ('Private', 'Private'), ('Walk', 'Walk')], default='Walk')
    bus_stop = models.ForeignKey(BusStop, on_delete=models.SET_NULL, null=True, blank=True)
    
    # Advanced Fee Collection
    advance_balance = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)
    
    phone_number = models.CharField(max_length=15, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.admin.first_name} {self.admin.last_name} - {self.course_id.name}"


# --- ACCOUNTS MODULE MODELS ---

class FeeHead(models.Model):
    """Types of Fees: Tuition, Admission, Exam, Transport, Hostel, etc."""
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name


class FeeStructure(models.Model):
    """Mapping FeeHeads to Courses with Amounts and Installments"""
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='course_fee_structures')
    fee_head = models.ForeignKey(FeeHead, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    installments = models.IntegerField(default=1)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('course', 'fee_head')

    def __str__(self):
        return f"{self.fee_head.name} - {self.course.name}"


class StudentInvoice(models.Model):
    """Individual Fee Demands generated for Students"""
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='student_invoices')
    fee_head = models.ForeignKey(FeeHead, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    due_date = models.DateField(null=True, blank=True)
    
    paid_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    is_paid = models.BooleanField(default=False)
    payment_date = models.DateField(null=True, blank=True) # Last payment date
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.student.admin.first_name} - {self.fee_head.name} - {self.amount}"


class FeePayment(models.Model):
    """Payment Transactions (Money In)"""
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='fee_payments')
    # Old direct link kept for history, but made optional. New method uses Allocations.
    invoice = models.ForeignKey(StudentInvoice, on_delete=models.SET_NULL, null=True, blank=True, related_name='invoice_payments')
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    payment_date = models.DateField(auto_now_add=True)
    payment_mode = models.CharField(max_length=50, default='Cash') # Cash, UPI, Bank Transfer
    remark = models.TextField(blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.student.admin.first_name} - {self.amount}"


class InvoiceAllocation(models.Model):
    """Links One Payment to One or More Invoices"""
    payment = models.ForeignKey(FeePayment, on_delete=models.CASCADE, related_name='allocations')
    invoice = models.ForeignKey(StudentInvoice, on_delete=models.CASCADE, related_name='allocations')
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"Pay #{self.payment.id} -> Inv #{self.invoice.id}: {self.amount}"


class ExpenseHead(models.Model):
    """Categories for Expenses e.g., Salary, Maintenance, Electricity"""
    name = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name


class Expense(models.Model):
    """Daily Expenses"""
    head = models.ForeignKey(ExpenseHead, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    date = models.DateField()
    description = models.TextField()
    added_by = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, null=True)
    receipt_file = models.FileField(upload_to='expense_receipts/', blank=True, null=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.head.name} - {self.amount}"


class Income(models.Model):
    """Other Incomes (Non-fee)"""
    source = models.CharField(max_length=200) # e.g. Donation, Rent
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    date = models.DateField()
    description = models.TextField(blank=True)
    added_by = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, null=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.source} - {self.amount}"


# ------------------------------


class Attendance(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    attendance_date = models.DateField()
    # session_year_id = models.ForeignKey(Session_year, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    # class Meta:
    #     unique_together = ('course', 'attendance_date', 'session_year_id')

    def __str__(self):
        return f"{self.course.name} - {self.attendance_date}"


class Attendance_Report(models.Model):
    student =models.ForeignKey(Student, on_delete=models.CASCADE)
    attendance = models.ForeignKey(Attendance, on_delete=models.CASCADE)
    is_present = models.BooleanField(default=False)
    leave_status = models.CharField(max_length=20, null=True, blank=True) # Informed, Not Informed
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.student.admin.first_name} - {self.attendance.attendance_date} - {'Present' if self.is_present else 'Absent'}"


class Student_Result(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE)
    exam = models.ForeignKey(Examination, on_delete=models.CASCADE, null=True, blank=True)
    ce_marks = models.FloatField(default=0, help_text='Continuous Evaluation marks')
    te_marks = models.FloatField(default=0, help_text='Term End marks')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = ('student', 'subject', 'exam')
    
    def total_marks(self):
        return self.ce_marks + self.te_marks
    
    def __str__(self):
        return f"{self.student.admin.first_name} - {self.subject.name} - {self.exam.name if self.exam else 'No Exam'} - Total: {self.total_marks()}"


class Student_Notification(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    message = models.TextField()
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"Notification for {self.student.admin.first_name}"


class Staff_Notification(models.Model):
    staff = models.ForeignKey(Staff, on_delete=models.CASCADE)
    message = models.TextField()
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"Notification for {self.staff.admin.first_name}"


class Student_leave(models.Model):
    STATUS_CHOICES = (
        (0, 'Pending'),
        (1, 'Approved'),
        (2, 'Rejected'),
    )
    
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    leave_date = models.DateField()
    leave_message = models.TextField()
    status = models.IntegerField(choices=STATUS_CHOICES, default=0)
    admin_remark = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.student.admin.first_name} - {self.leave_date} - {self.get_status_display()}"


class Staff_leave(models.Model):
    STATUS_CHOICES = (
        (0, 'Pending'),
        (1, 'Approved'),
        (2, 'Rejected'),
    )
    
    staff = models.ForeignKey(Staff, on_delete=models.CASCADE)
    leave_date = models.DateField()
    leave_message = models.TextField()
    status = models.IntegerField(choices=STATUS_CHOICES, default=0)
    admin_remark = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.staff.admin.first_name} - {self.leave_date} - {self.get_status_display()}"


class Student_Feedback(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    feedback = models.TextField()
    feedback_reply = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"Feedback from {self.student.admin.first_name}"


class Staff_Feedback(models.Model):
    staff = models.ForeignKey(Staff, on_delete=models.CASCADE)
    feedback = models.TextField()
    feedback_reply = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"Feedback from {self.staff.admin.first_name}"


class Enquiry(models.Model):
    name = models.CharField(max_length=100)
    place = models.CharField(max_length=100)
    district = models.CharField(max_length=100)
    phone_number = models.CharField(max_length=15)
    parent_name = models.CharField(max_length=100)
    course = models.ForeignKey(Course, on_delete=models.SET_NULL, null=True)
    percentage = models.FloatField()
    type_of_admission = models.CharField(max_length=50)
    token = models.CharField(max_length=50, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.name} - {self.token}"


class News(models.Model):
    title = models.CharField(max_length=200)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name_plural = 'News'
        ordering = ['-created_at']
    
    def __str__(self):
        return self.title


# Signals to auto-create profiles
@receiver(post_save, sender=CustomUser)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        if instance.user_type == 2:  # Staff
            Staff.objects.create(
                admin=instance,
                address='',
                gender='Male'
            )
        elif instance.user_type == 4: # Accountant
            Accountant.objects.create(
                admin=instance,
                address='',
                gender='Male'
            )
        elif instance.user_type == 5: # Management
            Management.objects.create(
                admin=instance,
                address=''
            )
        elif instance.user_type == 3:  # Student
            # Student is created manually in views usually
            pass
    else:
        # Save profiles if they exist and user is updated
        if instance.user_type == 2:
            instance.staff.save()
        elif instance.user_type == 4:
            instance.accountant.save()
        elif instance.user_type == 5:
            instance.management.save()


@receiver(post_save, sender=Student)
def create_student_invoices(sender, instance, created, **kwargs):
    if created:
        # Fetch Fee Structures for the Course
        try:
            structures = FeeStructure.objects.filter(course=instance.course_id)
            for structure in structures:
                head_name = structure.fee_head.name.lower()
                amount_to_charge = structure.amount
                
                # Conditional Checks
                if 'hostel' in head_name:
                    if not instance.uses_hostel:
                        continue
                        
                if 'transport' in head_name or 'bus' in head_name:
                    if not instance.uses_transport:
                        continue
                    # Bus Stop Override
                    if instance.bus_stop and instance.bus_stop.monthly_fee > 0:
                        amount_to_charge = instance.bus_stop.monthly_fee
                        
                # Create Invoice
                StudentInvoice.objects.create(
                    student=instance,
                    fee_head=structure.fee_head,
                    amount=amount_to_charge,
                    due_date=datetime.date.today() + datetime.timedelta(days=30) # Default Due Date: 30 days
                )
        except Exception as e:
            print(f"Error generating auto-invoices: {e}")

