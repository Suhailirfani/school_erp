from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from hadiya.models import FeePayment, StudentInvoice, Expense, Income, FeeHead, FeeStructure, Course, Student

def accountant_required(view_func):
    """Decorator to ensure only Accountant can access views"""
    @login_required
    def wrapper(request, *args, **kwargs):
        if request.user.user_type not in [1, 4]:
            messages.error(request, 'Access denied. Accountant privileges required.')
            return redirect('login')
        return view_func(request, *args, **kwargs)
    return wrapper

@accountant_required
def accountant_dashboard(request):
    """Accountant Dashboard"""
    context = {
        'page_title': 'Accountant Dashboard'
    }
    return render(request, 'Accountant/home.html', context)

# --- Fee Head Management ---

@accountant_required
def manage_fee_head(request):
    """List all Fee Heads"""
    fee_heads = FeeHead.objects.all()
    context = {
        'fee_heads': fee_heads,
        'page_title': 'Manage Fee Heads'
    }
    return render(request, 'Accountant/manage_fee_head.html', context)

@accountant_required
def add_fee_head(request):
    """Add a new Fee Head"""
    if request.method == 'POST':
        name = request.POST.get('name')
        description = request.POST.get('description')
        
        try:
            FeeHead.objects.create(name=name, description=description)
            messages.success(request, "Fee Head Added Successfully!")
            return redirect('manage_fee_head')
        except Exception as e:
            messages.error(request, f"Error: {e}")
            
    context = {
        'page_title': 'Add Fee Head'
    }
    return render(request, 'Accountant/add_fee_head.html', context)

@accountant_required
def edit_fee_head(request, fee_head_id):
    """Edit Fee Head"""
    fee_head = get_object_or_404(FeeHead, id=fee_head_id)
    if request.method == 'POST':
        try:
            fee_head.name = request.POST.get('name')
            fee_head.description = request.POST.get('description')
            fee_head.save()
            messages.success(request, "Fee Head Updated Successfully!")
            return redirect('manage_fee_head')
        except Exception as e:
            messages.error(request, f"Error: {e}")
            
    context = {
        'fee_head': fee_head,
        'page_title': 'Edit Fee Head'
    }
    return render(request, 'Accountant/edit_fee_head.html', context)

@accountant_required
def delete_fee_head(request, fee_head_id):
    """Delete Fee Head"""
    try:
        fee_head = FeeHead.objects.get(id=fee_head_id)
        fee_head.delete()
        messages.success(request, "Fee Head Deleted Successfully!")
    except Exception as e:
        messages.error(request, f"Error: {e}")
    return redirect('manage_fee_head')


# --- Fee Structure Management ---

@accountant_required
def manage_fee_structure(request):
    """List all Fee Structures"""
    structures = FeeStructure.objects.all().select_related('course', 'fee_head')
    context = {
        'structures': structures,
        'page_title': 'Manage Fee Structures'
    }
    return render(request, 'Accountant/manage_fee_structure.html', context)

@accountant_required
def add_fee_structure(request):
    """Add Fee Structure (Assign Fee to Course)"""
    courses = Course.objects.all()
    fee_heads = FeeHead.objects.all()
    
    if request.method == 'POST':
        course_id = request.POST.get('course_id')
        fee_head_id = request.POST.get('fee_head_id')
        amount = request.POST.get('amount')
        installments = request.POST.get('installments')
        
        try:
            course = Course.objects.get(id=course_id)
            fee_head = FeeHead.objects.get(id=fee_head_id)
            
            # Check if exists
            if FeeStructure.objects.filter(course=course, fee_head=fee_head).exists():
                messages.error(request, "Fee Structure already exists for this Course and Fee Head")
            else:
                FeeStructure.objects.create(
                    course=course,
                    fee_head=fee_head,
                    amount=amount,
                    installments=installments
                )
                messages.success(request, "Fee Structure Added Successfully!")
                return redirect('manage_fee_structure')
                
        except Exception as e:
            messages.error(request, f"Error: {e}")
            
    context = {
        'courses': courses,
        'fee_heads': fee_heads,
        'page_title': 'Add Fee Structure'
    }
    return render(request, 'Accountant/add_fee_structure.html', context)

@accountant_required
def edit_fee_structure(request, structure_id):
    """Edit Fee Structure"""
    structure = get_object_or_404(FeeStructure, id=structure_id)
    courses = Course.objects.all()
    fee_heads = FeeHead.objects.all()
    
    if request.method == 'POST':
        try:
            structure.amount = request.POST.get('amount')
            structure.installments = request.POST.get('installments')
            # Assuming we don't change Course/Head in edit, only amounts
            structure.save()
            messages.success(request, "Fee Structure Updated Successfully!")
            return redirect('manage_fee_structure')
        except Exception as e:
            messages.error(request, f"Error: {e}")
            
    context = {
        'structure': structure,
        'courses': courses,
        'fee_heads': fee_heads,
        'page_title': 'Edit Fee Structure'
    }
    return render(request, 'Accountant/edit_fee_structure.html', context)

@accountant_required
def delete_fee_structure(request, structure_id):
    """Delete Fee Structure"""
    try:
        structure = FeeStructure.objects.get(id=structure_id)
        structure.delete()
        messages.success(request, "Fee Structure Deleted Successfully!")
    except Exception as e:
        messages.error(request, f"Error: {e}")
    return redirect('manage_fee_structure')


# --- Fee Generation & Collection ---

@accountant_required
def generate_invoice(request):
    """Generate Invoices for Students based on Fee Structure"""
    courses = Course.objects.all()
    if request.method == 'POST':
        course_id = request.POST.get('course_id')
        try:
            course = Course.objects.get(id=course_id)
            students = Student.objects.filter(course_id=course)
            fee_structures = FeeStructure.objects.filter(course=course)
            
            count = 0
            for student in students:
                for fee in fee_structures:
                    # Logic for conditional fees
                    head_name = fee.fee_head.name.lower()
                    amount_to_charge = fee.amount
                    
                    if 'hostel' in head_name:
                        if not student.uses_hostel:
                            continue
                            
                    if 'transport' in head_name or 'bus' in head_name:
                        if not student.uses_transport:
                            continue
                        # Use Bus Stop fee if higher/different? 
                        # User requirement: "bus stop... monthly fee". 
                        # We override fee structure amount with bus stop fee if available.
                        if student.bus_stop and student.bus_stop.monthly_fee > 0:
                            amount_to_charge = student.bus_stop.monthly_fee
                    
                    # Create Invoice if not exists (One-time check for simplicity in this MVP)
                    # For a real system, we'd need 'Term' or 'Month' tracking.
                    if not StudentInvoice.objects.filter(student=student, fee_head=fee.fee_head).exists():
                         StudentInvoice.objects.create(
                             student=student,
                             fee_head=fee.fee_head,
                             amount=amount_to_charge
                         )
                         count += 1
            
            messages.success(request, f"Generated {count} Invoices for {course.name}")
        except Exception as e:
            messages.error(request, f"Error: {e}")
            
    context = {
        'courses': courses,
        'page_title': 'Generate Invoices'
    }
    return render(request, 'Accountant/generate_invoice.html', context)

@accountant_required
def print_invoice(request, payment_id):
    """Print Payment Receipt"""
    payment = get_object_or_404(FeePayment, id=payment_id)
    allocations = payment.allocations.all()
    return render(request, 'Accountant/print_invoice.html', {
        'payment': payment,
        'allocations': allocations
    })
    

# --- Expense Management ---

@accountant_required
def manage_expense_head(request):
    """Manage Expense Categories"""
    heads = ExpenseHead.objects.all()
    if request.method == 'POST':
        name = request.POST.get('name')
        try:
            ExpenseHead.objects.create(name=name)
            messages.success(request, "Expense Head Added!")
            return redirect('manage_expense_head')
        except Exception as e:
            messages.error(request, f"Error: {e}")
            
    return render(request, 'Accountant/manage_expense_head.html', {'heads': heads, 'page_title': 'Expense Heads'})

@accountant_required
def add_expense(request):
    """Add New Expense"""
    heads = ExpenseHead.objects.all()
    if request.method == 'POST':
        head_id = request.POST.get('head_id')
        amount = request.POST.get('amount')
        date = request.POST.get('date')
        description = request.POST.get('description')
        receipt_file = request.FILES.get('receipt_file')
        
        try:
            head = ExpenseHead.objects.get(id=head_id)
            Expense.objects.create(
                head=head,
                amount=amount,
                date=date,
                description=description,
                added_by=request.user,
                receipt_file=receipt_file
            )
            messages.success(request, "Expense Added Successfully!")
            return redirect('manage_expense')
        except Exception as e:
            messages.error(request, f"Error: {e}")
            
    return render(request, 'Accountant/add_expense.html', {'heads': heads, 'page_title': 'Add Expense'})

@accountant_required
def manage_expense(request):
    """List Expenses"""
    expenses = Expense.objects.all().order_by('-date')
    return render(request, 'Accountant/manage_expense.html', {'expenses': expenses, 'page_title': 'Manage Expenses'})


# --- Income Management ---

@accountant_required
def manage_income(request):
    """List Incomes"""
    incomes = Income.objects.all().order_by('-date')
    return render(request, 'Accountant/manage_income.html', {'incomes': incomes, 'page_title': 'Manage Incomes'})

@accountant_required
def add_income(request):
    """Add New Income"""
    if request.method == 'POST':
        source = request.POST.get('source')
        amount = request.POST.get('amount')
        date = request.POST.get('date')
        description = request.POST.get('description')
        
        try:
            Income.objects.create(
                source=source,
                amount=amount,
                date=date,
                description=description,
                added_by=request.user
            )
            messages.success(request, "Income Added Successfully!")
            return redirect('manage_income')
        except Exception as e:
            messages.error(request, f"Error: {e}")
            
    return render(request, 'Accountant/add_income.html', {'page_title': 'Add Income'})

@accountant_required
def fee_collection(request):
    """Search Student and Pay Fees (Advanced)"""
    from hadiya.models import InvoiceAllocation
    import datetime
    
    students = Student.objects.all()
    invoices = None
    student_obj = None
    
    # Handle Student Selection (Persistent)
    student_id = request.POST.get('student_id') or request.GET.get('student_id')
    if student_id:
        try:
            student_obj = Student.objects.get(admin__id=student_id)
            invoices = StudentInvoice.objects.filter(student=student_obj).order_by('created_at') # Oldest first for auto-allocation
        except Student.DoesNotExist:
            messages.error(request, "Student Not Found")
            
    if request.method == 'POST' and 'pay_fee' in request.POST:
        try:
            amount_paid = float(request.POST.get('amount_paid'))
            payment_mode = request.POST.get('payment_mode', 'Cash')
            remark = request.POST.get('remark', '')
            
            # 1. Create Transaction
            payment = FeePayment.objects.create(
                student=student_obj,
                amount=amount_paid,
                payment_mode=payment_mode,
                remark=remark
            )
            
            # 2. Allocation Logic (Auto - Oldest Dues First)
            # Future: Add Manual Allocation Mode handling here
            
            remaining_payment = amount_paid
            
            # Fetch unpaid invoices
            unpaid_invoices = StudentInvoice.objects.filter(student=student_obj, is_paid=False).order_by('created_at')
            
            for invoice in unpaid_invoices:
                if remaining_payment <= 0:
                    break
                    
                due_amount = float(invoice.amount) - float(invoice.paid_amount)
                
                # Determine how much to pay for this invoice
                allocation_amount = min(remaining_payment, due_amount)
                
                # Update Invoice
                invoice.paid_amount = float(invoice.paid_amount) + allocation_amount
                if invoice.paid_amount >= float(invoice.amount):
                    invoice.is_paid = True
                    invoice.payment_date = datetime.date.today()
                invoice.save()
                
                # Create Allocation Record
                InvoiceAllocation.objects.create(
                    payment=payment,
                    invoice=invoice,
                    amount=allocation_amount
                )
                
                remaining_payment -= allocation_amount
            
                # 3. Handle Surplus -> Advance Balance
            if remaining_payment > 0:
                student_obj.advance_balance = float(student_obj.advance_balance) + remaining_payment
                student_obj.save()
                messages.success(request, f"Payment Successful! {remaining_payment} added to Advance Balance.")
            else:
                messages.success(request, "Payment Successful!")
                
            # Redirect to Print Receipt
            return redirect('print_invoice', payment_id=payment.id)
            
        except Exception as e:
            messages.error(request, f"Error: {e}")

    context = {
        'students': students,
        'invoices': invoices,
        'selected_student': student_obj,
        'page_title': 'Collect Fees'
    }
    return render(request, 'Accountant/fee_collection.html', context)


# --- Reports ---

@accountant_required
def daily_collection_report(request):
    """Daily Fee Collection Report"""
    import datetime
    date_str = request.GET.get('date', datetime.date.today().strftime('%Y-%m-%d'))
    
    try:
        selected_date = datetime.datetime.strptime(date_str, '%Y-%m-%d').date()
        payments = FeePayment.objects.filter(payment_date=selected_date)
        total_collection = sum(p.amount for p in payments)
    except ValueError:
        payments = []
        total_collection = 0
        messages.error(request, "Invalid Date Format")
        
    context = {
        'payments': payments,
        'selected_date': date_str,
        'total_collection': total_collection,
        'page_title': 'Daily Collection Report'
    }
    return render(request, 'Accountant/daily_collection_report.html', context)

@accountant_required
def expense_reports(request):
    """Expense Reports"""
    import datetime
    from django.db.models import Sum
    
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')
    expenses = []
    total_expense = 0
    
    if start_date and end_date:
        expenses = Expense.objects.filter(date__range=[start_date, end_date])
        total_expense = expenses.aggregate(Sum('amount'))['amount__sum'] or 0
        
    context = {
        'expenses': expenses,
        'start_date': start_date,
        'end_date': end_date,
        'total_expense': total_expense,
        'page_title': 'Expense Reports'
    }
    return render(request, 'Accountant/expense_reports.html', context)

@accountant_required
def outstanding_fees_report(request):
    """Outstanding Fees Report"""
    from django.db.models import F, Sum
    
    # Filter invoices where paid_amount < amount
    # We can also filter by Course if needed (add filter form)
    
    pending_invoices = StudentInvoice.objects.filter(is_paid=False).annotate(
        balance=F('amount') - F('paid_amount')
    ).select_related('student', 'fee_head')
    
    total_outstanding = sum(inv.balance for inv in pending_invoices)
    
    context = {
        'pending_invoices': pending_invoices,
        'total_outstanding': total_outstanding,
        'page_title': 'Outstanding Fees Report'
    }
    return render(request, 'Accountant/outstanding_fees_report.html', context)
