from django.contrib import admin
from .models import FeeCategory, StudentFeeStructure, FeePayment, AccountLedger, MonthlyFeeUpdate


class FeeCategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'is_recurring', 'created_at')
    list_filter = ('is_recurring',)
    search_fields = ('name', 'description')


class StudentFeeStructureAdmin(admin.ModelAdmin):
    list_display = ('student', 'fee_category', 'amount', 'due_date', 'is_paid')
    list_filter = ('fee_category', 'is_paid')
    search_fields = ('student__admin__first_name', 'student__admin__last_name', 'student__admin__email')


class FeePaymentAdmin(admin.ModelAdmin):
    list_display = ('receipt_number', 'student', 'fee_category', 'amount', 'payment_date', 'payment_method')
    list_filter = ('payment_method', 'payment_date', 'fee_category')
    search_fields = ('receipt_number', 'student__admin__first_name', 'student__admin__last_name', 'transaction_id')
    date_hierarchy = 'payment_date'


class AccountLedgerAdmin(admin.ModelAdmin):
    list_display = ('reference_number', 'transaction_type', 'category', 'amount', 'transaction_date')
    list_filter = ('transaction_type', 'category', 'transaction_date')
    search_fields = ('reference_number', 'description', 'category')
    date_hierarchy = 'transaction_date'


class MonthlyFeeUpdateAdmin(admin.ModelAdmin):
    list_display = ('student', 'month', 'year', 'total_amount', 'paid_amount', 'is_paid', 'due_date')
    list_filter = ('month', 'year', 'is_paid')
    search_fields = ('student__admin__first_name', 'student__admin__last_name')


admin.site.register(FeeCategory, FeeCategoryAdmin)
admin.site.register(StudentFeeStructure, StudentFeeStructureAdmin)
admin.site.register(FeePayment, FeePaymentAdmin)
admin.site.register(AccountLedger, AccountLedgerAdmin)
admin.site.register(MonthlyFeeUpdate, MonthlyFeeUpdateAdmin)
