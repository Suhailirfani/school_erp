from django.urls import path
from student_management_system import Accountant_views

urlpatterns = [
    path('', Accountant_views.accountant_dashboard, name='accountant_dashboard'),
    
    # Fee Heads
    path('manage_fee_head/', Accountant_views.manage_fee_head, name='manage_fee_head'),
    path('add_fee_head/', Accountant_views.add_fee_head, name='add_fee_head'),
    path('edit_fee_head/<int:fee_head_id>/', Accountant_views.edit_fee_head, name='edit_fee_head'),
    path('delete_fee_head/<int:fee_head_id>/', Accountant_views.delete_fee_head, name='delete_fee_head'),
    
    # Fee Structures
    path('manage_fee_structure/', Accountant_views.manage_fee_structure, name='manage_fee_structure'),
    path('add_fee_structure/', Accountant_views.add_fee_structure, name='add_fee_structure'),
    path('edit_fee_structure/<int:structure_id>/', Accountant_views.edit_fee_structure, name='edit_fee_structure'),
    path('delete_fee_structure/<int:structure_id>/', Accountant_views.delete_fee_structure, name='delete_fee_structure'),
    
    # Fee Collection
    path('generate_invoice/', Accountant_views.generate_invoice, name='generate_invoice'),
    path('fee_collection/', Accountant_views.fee_collection, name='fee_collection'),
    path('print_invoice/<int:payment_id>/', Accountant_views.print_invoice, name='print_invoice'),
    
    # Expenses
    path('manage_expense_head/', Accountant_views.manage_expense_head, name='manage_expense_head'),
    path('add_expense/', Accountant_views.add_expense, name='add_expense'),
    path('manage_expense/', Accountant_views.manage_expense, name='manage_expense'),
    
    # Incomes
    path('manage_income/', Accountant_views.manage_income, name='manage_income'),
    path('add_income/', Accountant_views.add_income, name='add_income'),
    
    # Reports
    path('daily_collection_report/', Accountant_views.daily_collection_report, name='daily_collection_report'),
    path('expense_reports/', Accountant_views.expense_reports, name='expense_reports'),
    path('outstanding_fees_report/', Accountant_views.outstanding_fees_report, name='outstanding_fees_report'),
]
