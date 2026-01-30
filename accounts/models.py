from django.db import models
from hadiya.models import Student, CustomUser


class FeeCategory(models.Model):
    """Categories of fees (e.g., Tuition, Admission, Bus Fee, Hostel Fee)"""
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)
    is_recurring = models.BooleanField(default=False, help_text='True if fee is charged monthly/yearly')
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name_plural = 'Fee Categories'
    
    def __str__(self):
        return self.name


class StudentFeeStructure(models.Model):
    """Fee structure assigned to each student"""
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='fee_structure')
    fee_category = models.ForeignKey(FeeCategory, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    due_date = models.DateField(null=True, blank=True)
    is_paid = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = ('student', 'fee_category')
        verbose_name = 'Student Fee Structure'
        verbose_name_plural = 'Student Fee Structures'
    
    def __str__(self):
        return f"{self.student.admin.first_name} - {self.fee_category.name} - Rs.{self.amount}"


class FeePayment(models.Model):
    """Record of fee payments made by students"""
    PAYMENT_METHOD_CHOICES = (
        ('Cash', 'Cash'),
        ('Card', 'Card'),
        ('UPI', 'UPI'),
        ('Bank Transfer', 'Bank Transfer'),
        ('Cheque', 'Cheque'),
    )
    
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='payments')
    fee_category = models.ForeignKey(FeeCategory, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    payment_date = models.DateField()
    payment_method = models.CharField(max_length=20, choices=PAYMENT_METHOD_CHOICES, default='Cash')
    transaction_id = models.CharField(max_length=100, blank=True, null=True)
    receipt_number = models.CharField(max_length=50, unique=True)
    remarks = models.TextField(blank=True)
    recorded_by = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, null=True, related_name='recorded_payments')
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = 'Fee Payment'
        verbose_name_plural = 'Fee Payments'
        ordering = ['-payment_date']
    
    def __str__(self):
        return f"Receipt {self.receipt_number} - {self.student.admin.first_name} - Rs.{self.amount}"


class AccountLedger(models.Model):
    """Account ledger for all financial transactions"""
    TRANSACTION_TYPE_CHOICES = (
        ('Income', 'Income'),
        ('Expense', 'Expense'),
    )
    
    transaction_type = models.CharField(max_length=10, choices=TRANSACTION_TYPE_CHOICES)
    category = models.CharField(max_length=100)
    description = models.TextField()
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    transaction_date = models.DateField()
    reference_number = models.CharField(max_length=50, unique=True)
    payment = models.ForeignKey(FeePayment, on_delete=models.SET_NULL, null=True, blank=True, related_name='ledger_entries')
    recorded_by = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = 'Account Ledger Entry'
        verbose_name_plural = 'Account Ledger'
        ordering = ['-transaction_date']
    
    def __str__(self):
        return f"{self.transaction_type} - {self.category} - Rs.{self.amount} on {self.transaction_date}"


class MonthlyFeeUpdate(models.Model):
    """Track monthly fee updates for recurring fees"""
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='monthly_fees')
    month = models.CharField(max_length=20)
    year = models.IntegerField()
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    paid_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    is_paid = models.BooleanField(default=False)
    due_date = models.DateField()
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ('student', 'month', 'year')
        verbose_name = 'Monthly Fee Update'
        verbose_name_plural = 'Monthly Fee Updates'
    
    def __str__(self):
        return f"{self.student.admin.first_name} - {self.month} {self.year}"
    
    def balance(self):
        return self.total_amount - self.paid_amount
