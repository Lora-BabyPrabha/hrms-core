# from .models import Muster, LeaveRequest, ExpenseClaim, LoanRequest

# def pending_requests(request):
#     if request.user.role == 'HR' or request.user.role == 'Manager' or request.user.is_superuser:
#         pending_musters = Muster.objects.filter(status='Pending')
#         pending_leave_requests = LeaveRequest.objects.filter(status='pending')
#         pending_expenses = ExpenseClaim.objects.filter(status='pending')
#         pending_loans = LoanRequest.objects.filter(status='pending')
#     else:
#         pending_musters = pending_leave_requests = pending_expenses = pending_loans = None
    
#     return {
#         'pending_musters': pending_musters,
#         'pending_leave_requests': pending_leave_requests,
#         'pending_expenses': pending_expenses,
#         'pending_loans': pending_loans,
#     }

# context_processors.py
from .models import Muster, LeaveRequest, ExpenseClaim, LoanRequest

def common_data(request):
    pending_musters = Muster.objects.filter(status='Pending')
    pending_leave_request = LeaveRequest.objects.filter(status='pending')
    pending_expense = ExpenseClaim.objects.filter(status='pending')
    pending_loan = LoanRequest.objects.filter(status='pending')

    return {
        'pending_musters': pending_musters,
        'pending_leave_request': pending_leave_request,
        'pending_expense': pending_expense,
        'pending_loan': pending_loan
    }
