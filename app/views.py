import calendar
from django.http import HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.contrib import messages
from django.contrib.auth import authenticate,login,logout
from django.contrib.auth.decorators import login_required
from app.models import *
from app.forms import *
from django.utils import timezone
from django.core.mail import send_mail
import random
from django.conf import settings
from app.decorators import *
from datetime import datetime, timedelta, date
from django.utils.dateparse import parse_date
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth import get_user_model
from django.http import HttpResponseForbidden
from django.contrib.admin.views.decorators import staff_member_required
from django.template.loader import render_to_string
from xhtml2pdf import pisa
from django.templatetags.static import static
from django.contrib.auth.decorators import login_required
from .models import Notification
from django.urls import reverse
from django.http import HttpResponse
from weasyprint import HTML
from .models import Employee, Salary
from django.conf import settings
from django.utils.timezone import now
from datetime import timedelta
from rest_framework.decorators import api_view
from rest_framework.response import Response
from .models import CustomUser, Employee, Performance
from .serializers import PerformanceSerializer
from datetime import timedelta
from django.shortcuts import render
from django.utils import timezone
from .models import TimeEntry, Muster, Holiday, LeaveRequest, Leave, CustomUser
from django.http import Http404
import calendar
from django.db.models import F
import re
from django.utils.timezone import now
from django.contrib.auth.hashers import make_password
import random
from django.core.mail import send_mail
from django.utils import timezone
import zoneinfo

CustomUser = get_user_model()


# Create your views here.

#------------------------------------------------------------- Index #

def indexview(request):

    if request.user.is_authenticated:
        return render(request, 'dashboard.html')
    
    else:

        if request.method == "POST":
            company_name = request.POST.get('company_name', '').strip()
            
            if company_name:
                company = Company_check.objects.filter(company_name__iexact=company_name).first()

                if company:
                    return redirect('login')
                
                else:
                    return render(request, 'index.html', {'message': 'No records found for the company.'})

    return render(request, 'index.html')


#------------------------------------------------------------- Login #

def loginview(request):
    if request.user.is_authenticated:
        return render(request, 'dashboard.html')

    if request.method == 'POST':
        employee_id = request.POST['username']  
        password = request.POST['password']

        try:
            user_obj = User.objects.get(employee_id=employee_id)
        except User.DoesNotExist:
            return render(request, 'login.html', {'message': 'User not found'})

        user = authenticate(request, employee_id=employee_id, password=password)

        if user is not None:
            login(request, user)
            return redirect("dashboard")
        else:
            return render(request, 'login.html', {'message': 'Incorrect Password'})

    return render(request, "login.html")


#------------------------------------------------------------- Search bar #

@login_required(login_url='/')
def search_results(request):
    query = request.GET.get('query', '').lower()

    normalized_query = query.replace('-', ' ').strip()

    page_urls = {
        'muster': 'muster',  
        'status': 'muster_status',  
        'leave': 'leave_balance',  
        'balance':'leave_balance',
        'holidays':'holidays',
        'salary': 'salary_details',  
        'expense': 'expense_claims',  
        'loan': 'loan_requests',  
        'task': 'task_management',
        'management':'task_management',
        'financial':'salary_details',
        'claim':'expense_claims',
        'tax':'tax_deduction',
        'deduction':'tax_deduction',
        'details':'profile',
        'edit':'profile',
        'personal':'profile',
        'professional':'profile',
        'banking':'profile',
        'picture':'profile',
        'profile':'profile',
        'cover':'profile',
        'data':'employee_requests',
    }
 
    if request.user.is_authenticated and request.user.role == 'HR' or request.user.role == 'Manager' or request.user.is_superuser:
        page_urls['request'] = 'employee_requests'

    for page_name, url_name in page_urls.items():
        normalized_page_name = page_name.lower().replace(' ', '-')

        if normalized_page_name in normalized_query:
            return redirect(reverse(url_name))  
 
    return redirect('dashboard')


#------------------------------------------------------------- FAQ #

@login_required(login_url='/')
def chat_bot(request):
    user = request.user
    employee = Employee.objects.get(employee_id=user.employee_id)
    return render(request,'chat_bot.html' , {'employee': employee})


#------------------------------------------------------------- Chat Bot #

@login_required(login_url='/')
def faq(request):
    user = request.user
    employee = Employee.objects.get(employee_id=user.employee_id)
    notifications = Notification.objects.filter(recipient=request.user, is_read=False).order_by('-created_at')[:5]

    return render(request,'faq.html' , {
        'employee': employee,
        'notifications': notifications,
        }
    )


#------------------------------------------------------------- Chat Bot #

@login_required(login_url='/')
def training(request):
    user = request.user
    employee = Employee.objects.get(employee_id=user.employee_id)
    notifications = Notification.objects.filter(recipient=request.user, is_read=False).order_by('-created_at')[:5]

    return render(request,'training.html' , {
        'employee': employee,
        'notifications': notifications,
        }
    )


#------------------------------------------------------------- Contact us #

@login_required(login_url='/')
def contact_us(request):
    user = request.user
    employee = Employee.objects.get(employee_id=user.employee_id)
    notifications = Notification.objects.filter(recipient=request.user, is_read=False).order_by('-created_at')[:5]

    return render(request,'contact_us.html' , {
        'employee': employee,
        'notifications': notifications,
        }
    )


#------------------------------------------------------------- Company records #

@login_required(login_url='/')
def company_check(request):
    return render(request,'company_check.html')


#------------------------------------------------------------- Company records #

@login_required(login_url='/')
def base(request):
    if user.role == 'Employee':
        user = request.user
        employee = Employee.objects.get(employee_id=user.employee_id)
        notifications = Notification.objects.filter(recipient=request.user, is_read=False).order_by('-created_at')[:5]
        return render(request, 'dashboard.html', {'employee': employee , 'notifications': notifications})

    elif user.role == 'HR' or user.role == 'Manager' or user.is_superuser:
        user = request.user
        notifications = Notification.objects.filter(recipient=request.user, is_read=False).order_by('-created_at')[:5]
        
        employee = Employee.objects.get(employee_id=user.employee_id)
        pending_musters = Muster.objects.filter(status='Pending')
        pending_leave_request = LeaveRequest.objects.filter(status='pending')
        pending_expense = ExpenseClaim.objects.filter(status='pending')
        pending_loan = LoanRequest.objects.filter(status='pending')
        return render(request, 'base.html', {
            'employee': employee,
            'pending_musters': pending_musters,
            'pending_leave_request': pending_leave_request,
            'pending_expense': pending_expense,
            'pending_loan': pending_loan,
            'notifications': notifications,
            }
        )
    
    return render(request,'base.html')


#------------------------------------------------------------- Dashboard #

@login_required(login_url='/')
def dashboard(request):
    if request.user.is_authenticated:
        user = request.user

        if user.role == 'Employee':

            # request for user #
            user = request.user
            employee = Employee.objects.get(employee_id=user.employee_id)

            # birthdays #
            today = datetime.now().date()
            today_month_day = today.strftime('%m-%d')
            employees_with_birthday = Employee.objects.filter(date_of_birth__month=today.month, date_of_birth__day=today.day)

            # notifications #
            notifications = Notification.objects.filter(recipient=request.user, is_read=False).order_by('-created_at')[:5]

            return render(request, 'dashboard.html', {'employee': employee , 'notifications': notifications, 'employees_with_birthday': employees_with_birthday, 'today': today})
        
        elif user.role == 'HR' or user.role == 'Manager' or user.is_superuser:

            user = request.user
            notifications = Notification.objects.filter(recipient=request.user, is_read=False).order_by('-created_at')[:5]
            today = datetime.now().date()
            today_month_day = today.strftime('%m-%d')
            employees_with_birthday = Employee.objects.filter(date_of_birth__month=today.month, date_of_birth__day=today.day)

            employee = Employee.objects.get(employee_id=user.employee_id)
            return render(request, 'dashboard.html', {
                'employee': employee,
                'employees_with_birthday': employees_with_birthday,
                'today': today,
                'notifications': notifications,
                
                }
            )

        return render(request, 'dashboard.html')
    
    else:
        return render(request,'index.html')
    

#------------------------------------------------------------- Employee requests - Notifications  #

@login_required(login_url='/')
@staff_member_required
def employee_requests(request):
    user = request.user
    muster_requests = Muster.objects.all()
    leave_requests = LeaveRequest.objects.all()
    expense_claims = ExpenseClaim.objects.all()
    loan_requests = LoanRequest.objects.all()
    time_entries = TimeEntry.objects.all()
    employees = CustomUser.objects.all()

    if request.method == 'POST':
        employee_id_input = request.POST.get('employee_id')
        selected_request_type = request.POST.get('request_type')

        if employee_id_input:
            try:
                employee = CustomUser.objects.get(employee_id=employee_id_input)
            except CustomUser.DoesNotExist:
                employee = None
        else:
            employee = None
 
        if selected_request_type == 'muster' or selected_request_type == '':
            if employee:
                muster_requests = Muster.objects.filter(user_id=employee.id)
                time_entries = TimeEntry.objects.filter(user_id=employee.id)
            else:
                muster_requests = Muster.objects.all()
                time_entries = TimeEntry.objects.all()
 
        if selected_request_type == 'leave' or selected_request_type == '':
            if employee:
                leave_requests = LeaveRequest.objects.filter(employee_id=employee.id)
            else:
                leave_requests = LeaveRequest.objects.all()
 
        if selected_request_type == 'expense' or selected_request_type == '':
            if employee:
                expense_claims = ExpenseClaim.objects.filter(employee_id=employee.id)
            else:
                expense_claims = ExpenseClaim.objects.all()
 
        if selected_request_type == 'loan' or selected_request_type == '':
            if employee:
                loan_requests = LoanRequest.objects.filter(employee_id=employee.id)
            else:
                loan_requests = LoanRequest.objects.all()
 
        if selected_request_type == 'time_entry' or selected_request_type == '':
            if employee:
                time_entries = TimeEntry.objects.filter(user_id=employee.id)
            else:
                time_entries = TimeEntry.objects.all()
 
    notifications = Notification.objects.filter(recipient=request.user, is_read=False).order_by('-created_at')[:5]
    employee = Employee.objects.get(employee_id=user.employee_id)

    if user.role == 'HR' or user.role == 'Manager' or user.is_superuser:
        user = request.user
        notifications = Notification.objects.filter(recipient=request.user, is_read=False).order_by('-created_at')[:5]
        

    return render(request, 'employee_data.html', {
        'employees': employees,
        'employee': employee,
        'muster_requests': muster_requests,
        'leave_requests': leave_requests,
        'expense_claims': expense_claims,
        'loan_requests': loan_requests,
        'time_entries': time_entries,
        'notifications': notifications,
    })


#------------------------------------------------------------- Mark as read -- Notifications  #

@login_required(login_url='/')
@staff_member_required
def staff_notifications(request):
    user = request.user
    employee = Employee.objects.get(employee_id=user.employee_id)

    musters = Muster.objects.filter(status='Pending')
    leaves = LeaveRequest.objects.filter(status='pending')
    expenses = ExpenseClaim.objects.filter(status='pending')
    pendings_loan = LoanRequest.objects.filter(status='pending')

    notifications = Notification.objects.filter(recipient=request.user, is_read=False).order_by('-created_at')[:5]

    if user.role == 'HR' or user.role == 'Manager' or user.is_superuser:
        user = request.user
        notifications = Notification.objects.filter(recipient=request.user, is_read=False).order_by('-created_at')[:5]
        

    return render(request, 'staff_notifications.html', {
        'employee': employee,
        'musters': musters,
        'leaves': leaves,
        'expenses': expenses,
        'pendings_loan': pendings_loan,
        'notifications': notifications,
    })



#------------------------------------------------------------- clock In #

@login_required(login_url='/')
def clock_in(request):
    if request.method == 'POST':
        latitude = request.POST.get('latitude')
        longitude = request.POST.get('longitude')

        if latitude and longitude:
            if TimeEntry.objects.filter(user=request.user, clock_out_time__isnull=True).exists():
                messages.warning(request, "You have already clocked in.")
            else:
                clock_in_time = timezone.now()
                time_entry = TimeEntry(
                    user=request.user,
                    clock_in_time=clock_in_time,
                    clock_in_latitude=latitude,
                    clock_in_longitude=longitude
                )
                time_entry.save()
                messages.success(request, "Clocked in successfully.")
        else:
            messages.error(request, "Unable to capture your location. Please try again.")
    
    return redirect('dashboard')
    

#------------------------------------------------------------- clock Out #

@login_required(login_url='/')
def clock_out(request):
    if request.method == 'POST':
        latitude = request.POST.get('latitude')
        longitude = request.POST.get('longitude')

        try:
            if latitude == '':
                latitude = None
            else:
                latitude = float(latitude)
        except ValueError:
            latitude = None
        
        try:
            if longitude == '':
                longitude = None
            else:
                longitude = float(longitude)
        except ValueError:
            longitude = None

        time_entry = TimeEntry.objects.filter(user=request.user, clock_out_time__isnull=True).first()

        if not time_entry:
            messages.warning(request, "You haven't clocked in yet.")
        else:
            clock_in_time = timezone.localtime(time_entry.clock_in_time)
            current_time = timezone.localtime(timezone.now())
            time_difference = current_time - clock_in_time

            if time_difference >= timedelta(hours=9):
                time_entry.clock_out_time = current_time
                time_entry.clock_out_latitude = latitude
                time_entry.clock_out_longitude = longitude
                time_entry.save()
                messages.success(request, "Clocked out successfully.")
            else:
                messages.warning(request, "You can only clock out after 9 hours.")

    return redirect('dashboard')


#------------------------------------------------------------- Muster #

@login_required(login_url='/')
def muster(request):
    user = request.user
    today_date = timezone.localtime(timezone.now()).date()
    today_date_str = today_date.strftime('%Y-%m-%d')
    clock_in_time = None
    time_entry = TimeEntry.objects.filter(user=user, clock_in_time__date=today_date).first()
 
    if time_entry:
        clock_in_time = timezone.localtime(time_entry.clock_in_time)
    else:
        print(f"No TimeEntry found for user {user} on {today_date}")
 
    if request.method == "POST":
        user = request.user
        employee_id = request.POST['employee_id']
        date_str = request.POST['date']
        clock_in_time = request.POST['clock_in_time']
        clock_out_time = request.POST['clock_out_time']
        reason = request.POST['reason']
        notes = request.POST['notes']
 
        date_obj = datetime.strptime(date_str, "%Y-%m-%d").date()
 
        muster_entry = Muster.objects.create(user=request.user,employee_id=employee_id,date=date_obj,clock_in_time=clock_in_time,clock_out_time=clock_out_time,reason=reason,notes=notes,status="Pending")

        notification_message = f"Your Muster request of {reason}, {date_obj} - {clock_in_time} & {clock_out_time} has been submitted successfully."
        Notification.objects.create(recipient=muster_entry.user, message=notification_message)
 
        muster_entry.save()

        return redirect('muster')
   
    user = request.user
    muster_entry = Muster.objects.filter(employee_id=user.employee_id)
    employee = Employee.objects.get(employee_id=user.employee_id)
    notifications = Notification.objects.filter(recipient=request.user, is_read=False).order_by('-created_at')[:5]

    return render(request,'muster.html', {
        'employee': employee,
        'employee_id': user.employee_id,
        "muster_entry": muster_entry,
        'today_date': today_date_str,
        'clock_in_time': clock_in_time,
        'notifications': notifications,
        }
    )


@login_required(login_url='/')
def muster_status(request):
    user = request.user

    time_entries = TimeEntry.objects.filter(user=user)

    entries = []
    for entry in time_entries:
        if entry.clock_in_time and entry.clock_out_time:
            time_difference = entry.clock_out_time - entry.clock_in_time

            if time_difference > timedelta(hours=12):
                continue

            status = "Regular" if time_difference >= timedelta(hours=9) else "Pending"
        else:
            status = "Pending"

        entries.append({
            "employee_id": entry.user.employee_id,
            "date": entry.clock_in_time.date() if entry.clock_in_time else None,
            "clock_in_time": entry.clock_in_time if entry.clock_in_time else None,
            "clock_out_time": entry.clock_out_time if entry.clock_out_time else None,
            "status": status,
        })

    user = request.user
    employee = Employee.objects.get(employee_id=user.employee_id)
    notifications = Notification.objects.filter(recipient=request.user, is_read=False).order_by('-created_at')[:5]

    return render(request, "muster_status.html", {
        "entries": entries,
        "employee": employee,
        'notifications': notifications,
        }
    )


#------------------------------------------------------------- Leave Request #

@login_required(login_url='/')
def leave_balance(request):
    user = request.user
    leave_request = LeaveRequest.objects.filter(employee=user)
    leave = Leave.objects.get(employee=request.user)
    employee = Employee.objects.get(employee_id=user.employee_id)
    notifications = Notification.objects.filter(recipient=request.user, is_read=False).order_by('-created_at')[:5]
    return render(request, 'leave_balance.html', {'leave': leave , 'leave_request': leave_request , "employee": employee , 'notifications': notifications})
 

@login_required(login_url='/')
def leave_request(request):
    if request.method == 'POST':
        leave_type = request.POST['leave_type']
        start_date = request.POST['start_date']
        end_date = request.POST['end_date']
        reason = request.POST['reason']

        start_date = datetime.strptime(start_date, "%Y-%m-%d").date()
        end_date = datetime.strptime(end_date, "%Y-%m-%d").date()

        weekdays_requested = 0
        current_day = start_date
        while current_day <= end_date:
            if current_day.weekday() < 5:
                weekdays_requested += 1
            current_day += timedelta(days=1)

        leave_request = LeaveRequest(
            employee=request.user,
            leave_type=leave_type,
            start_date=start_date,
            end_date=end_date,
            reason=reason,
            days_requested=weekdays_requested,
            status='pending'
        )
        notification_message = f"Your Leave Request of {leave_type} from {start_date} to {end_date} has been submitted successfully."
        Notification.objects.create(recipient=leave_request.employee, message=notification_message)
        leave_request.save()
 
        return redirect('leave_balance')
   
    user = request.user
    employee = Employee.objects.get(employee_id=user.employee_id)
    notifications = Notification.objects.filter(recipient=request.user, is_read=False).order_by('-created_at')[:5]
    return render(request, 'leave_request.html', {"employee": employee , 'notifications': notifications})


#------------------------------------------------------------- Holidays #

@login_required(login_url='/')
def holidays(request):
    if request.user.is_authenticated:
        h = Holiday.objects.all()
        user = request.user
        employee = Employee.objects.get(employee_id=user.employee_id)
        notifications = Notification.objects.filter(recipient=request.user, is_read=False).order_by('-created_at')[:5]
        
        return render(request, 'holidays.html',{
            'h': h,
            'employee': employee,
            'notifications': notifications,
            }
        )


#------------------------------------------------------------- Salary details #
    
@login_required(login_url='/')
def salary_details(request):
    user = request.user
    employee = Employee.objects.get(employee_id=user.employee_id)
 
    from_month = request.GET.get('from_month')
    to_month = request.GET.get('to_month')
 
    if not from_month and not to_month:
        latest_payslip = Salary.objects.filter(employee=employee).order_by('-month').first()
 
        if latest_payslip:
            from_month = latest_payslip.month.strftime('%Y-%m')
            to_month = latest_payslip.month.strftime('%Y-%m')
 
    if from_month:
        from_month = f"{from_month}-01"
 
    if to_month:
        to_month_date = datetime.strptime(f"{to_month}-01", '%Y-%m-%d')
        last_day_of_month = calendar.monthrange(to_month_date.year, to_month_date.month)[1]
        to_month = f"{to_month}-{last_day_of_month}"
 
    if from_month and to_month:
        payslips = Salary.objects.filter(
            employee=employee,
            month__gte=from_month,
            month__lte=to_month
        ).order_by('-month')
    else:
        payslips = Salary.objects.filter(employee=employee).order_by('-month')[:1]
 
    logo_url = request.build_absolute_uri(static('Lora.jpg'))
 
    return render(request, 'salary_details.html', {
        'employee': employee,
        'payslips': payslips,
        'logo_url': logo_url,
        'from_month': from_month[:7] if from_month else None,
        'to_month': to_month[:7] if to_month else None,
    })
 
 
def generate_payslip_pdf(request, employee_id):
    employee = get_object_or_404(Employee, employee_id=request.user.employee_id)

    from_month = request.GET.get('from_month')
    to_month = request.GET.get('to_month')

    if not from_month and not to_month:
        latest_payslip = Salary.objects.filter(employee=employee).order_by('-month').first()
 
        if latest_payslip:
            from_month = latest_payslip.month.strftime('%Y-%m')
            to_month = latest_payslip.month.strftime('%Y-%m')

    if from_month:
        from_month = f"{from_month}-01"

    if to_month:
        to_month_date = datetime.strptime(f"{to_month}-01", '%Y-%m-%d')
        last_day_of_month = calendar.monthrange(to_month_date.year, to_month_date.month)[1]
        to_month = f"{to_month}-{last_day_of_month}"

    if from_month and to_month:
        payslips = Salary.objects.filter(
            employee=employee,
            month__gte=from_month,
            month__lte=to_month
        ).order_by('-month')
    else:
        payslips = Salary.objects.filter(employee=employee).order_by('-month')[:1]

    logo_url = request.build_absolute_uri(static('salary_logo_40.png'))

    html_string = render_to_string('all_payslips.html', {
        'employee': employee,
        'payslips': payslips,
        'logo_url': logo_url
    })

    pdf = HTML(string=html_string, base_url=request.build_absolute_uri()).write_pdf()
    response = HttpResponse(pdf, content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="{employee.user.username}_payslips.pdf"'
 
    return response


#------------------------------------------------------------- Tax Deduction #

@login_required(login_url='/')
def tax_deduction(request):
    user = request.user
    td = LoanRequest.objects.filter(employee=user)
    employee = Employee.objects.get(employee_id=user.employee_id)
    notifications = Notification.objects.filter(recipient=request.user, is_read=False).order_by('-created_at')[:5]

    return render(request, 'tax_deduction.html', {
        'user': user,
        'td': td,
        'employee': employee,
        'notifications': notifications,
        }
    )


#------------------------------------------------------------- Forgot Password #

User = get_user_model()
 
def generate_otp():
    """Generate a 6-digit OTP"""
    return random.randint(100000, 999999)
 
def forgot_password(request):
    if request.method == 'POST':
        form = ForgotPasswordForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            try:
                user = User.objects.get(email=email)
            except User.DoesNotExist:
                messages.error(request, "Email address not found.")
                return redirect('forgot_password')
 
            otp = generate_otp()

            india_tz = zoneinfo.ZoneInfo('Asia/Kolkata')
            current_time = datetime.now(india_tz)

            request.session['otp'] = str(otp)
            request.session['otp_time'] = current_time.strftime('%Y-%m-%d %H:%M:%S%z')
            request.session['user_email'] = email
 
            send_mail(
                'Password Reset OTP',
                f'Your OTP for password reset is {otp}. It is valid for 10 minutes.',
                'your-email@gmail.com',
                [email],
                fail_silently=False,
            )
 
            messages.success(request, "OTP sent to your email address.")
            return redirect('verify_otp')
    else:
        form = ForgotPasswordForm()
 
    return render(request, 'forgot_password.html', {'form': form})
 
def verify_otp(request):
    if request.method == 'POST':
        otp_input = request.POST.get('otp')
        stored_otp = request.session.get('otp')
        stored_otp_time_str = request.session.get('otp_time')
        user_email = request.session.get('user_email')
 
        if not all([stored_otp, stored_otp_time_str, user_email]):
            messages.error(request, "Session expired. Please request a new OTP.")
            return redirect('forgot_password')
 
        try:
            india_tz = zoneinfo.ZoneInfo('Asia/Kolkata')
            stored_time = datetime.strptime(stored_otp_time_str, '%Y-%m-%d %H:%M:%S%z')
            current_time = datetime.now(india_tz)

            time_diff = (current_time - stored_time).total_seconds() / 60

            if time_diff > 10:
                messages.error(request, "OTP has expired. Please request a new one.")

                for key in ['otp', 'otp_time', 'user_email']:
                    request.session.pop(key, None)
                return redirect('forgot_password')

            if otp_input == stored_otp:
                messages.success(request, "OTP verified successfully.")
                return redirect('reset_password_with_otp')
            else:
                messages.error(request, "Invalid OTP. Please try again.")
                return redirect('verify_otp')
 
        except Exception as e:
            messages.error(request, "An error occurred. Please try again.")
            return redirect('forgot_password')
 
    return render(request, 'verify_otp.html')
 
 
def reset_password_with_otp(request):
    if request.method == 'POST':
        new_password = request.POST.get('new_password')
        confirm_password = request.POST.get('confirm_password')
        user_email = request.session.get('user_email')

        if new_password != confirm_password:
            messages.error(request, "Passwords do not match. Please try again.")
            return redirect('reset_password_with_otp')

        password_regex = r'^(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]{8,}$'
 
        if not re.match(password_regex, new_password):
            messages.error(request, (
                "Password must be at least 8 characters long, contain at least one uppercase letter, "
                "one special character, and one number."
            ))
            return redirect('reset_password_with_otp')

        try:
            user = get_user_model().objects.get(email=user_email)
            user.password = make_password(new_password)
            user.password_last_changed = now()
            user.save()

            for key in ['otp', 'otp_time', 'user_email']:
                request.session.pop(key, None)
 
            messages.success(request, "Password reset successful. You can now log in with your new password.")
            return redirect('login')
        except get_user_model().DoesNotExist:
            messages.error(request, "No user found with this email address.")
            return redirect('forgot_password')
        except Exception as e:
            messages.error(request, f"An error occurred: {str(e)}")
            return redirect('forgot_password')
 
    return render(request, 'reset_password_with_otp.html')


#------------------------------------------------------------- Reset Password #

from django.contrib.auth import update_session_auth_hash
 
def reset_password(request):
    if request.method == 'POST':
        form = ResetPasswordForm(request.POST)
        if form.is_valid():
            employee_id = form.cleaned_data['employee_id']
            old_password = form.cleaned_data['old_password']
            new_password = form.cleaned_data['new_password']
 
            try:
                user = CustomUser.objects.get(employee_id=employee_id)
                if user.check_password(old_password):
                    user.set_password(new_password)
                    user.password_last_changed = timezone.now()
 
                    user.save()
                    update_session_auth_hash(request, user)
                    messages.success(request, "Your password has been updated successfully.")
                    return redirect('login')
                else:
                    messages.error(request, "Old password is incorrect.")
            except CustomUser.DoesNotExist:
                messages.error(request, "User with this employee ID does not exist.")
    else:
        form = ResetPasswordForm()
 
    return render(request, 'reset_password.html', {'form': form})
 
    
#------------------------------------------------------------- Profile #

@login_required(login_url='/')
def profile_view(request):
    user = request.user
    employee = Employee.objects.get(employee_id=user.employee_id)
    notifications = Notification.objects.filter(recipient=request.user, is_read=False).order_by('-created_at')[:5]
    print('===', employee.name, '===')

    return render(request, 'profile.html', {
        'user': user,
        'employee': employee,
        'notifications': notifications,
        }
    )


@login_required(login_url='/')
def edit_personal_info(request, employee_id):
    employee = get_object_or_404(Employee, id=employee_id)

    if request.user.employee_user != employee:
        messages.error(request, "You don't have permission to edit this profile.")
        return redirect('profile')
   
    if request.method == 'POST':
        form = PersonalInfoForm(request.POST, instance=employee)
        if form.is_valid():
            form.save()
            messages.success(request, 'Personal information updated successfully!')
            return render(request, 'edit_personal_info.html', {
                'form': PersonalInfoForm(instance=employee),
                'employee': employee
            })
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = PersonalInfoForm(instance=employee)
   
    return render(request, 'edit_personal_info.html', {
        'form': form,
        'employee': employee
    })


@login_required(login_url='/')
def edit_professional_info(request, employee_id):
    employee = get_object_or_404(Employee, employee_id=request.user.employee_id)
    
    if request.method == 'POST':
        form = ProfessionalInfoForm(request.POST, instance=employee)
        if form.is_valid():
            form.save()
            return redirect('profile')
    else:
        form = ProfessionalInfoForm(instance=employee)
    
    user = request.user
    employee = Employee.objects.get(employee_id=user.employee_id)
    notifications = Notification.objects.filter(recipient=request.user, is_read=False).order_by('-created_at')[:5]

    return render(request, 'edit_professional_info.html', {
        'form': form,
        'employee': employee,
        'notifications': notifications,
        }
    )


@login_required(login_url='/')
def edit_banking_info(request, employee_id):
    employee = get_object_or_404(Employee, employee_id=request.user.employee_id)
    
    if request.method == 'POST':
        form = BankingInfoForm(request.POST, instance=employee)
        if form.is_valid():
            form.save()
            return redirect('profile')
    else:
        form = BankingInfoForm(instance=employee)
    
    user = request.user
    employee = Employee.objects.get(employee_id=user.employee_id)
    notifications = Notification.objects.filter(recipient=request.user, is_read=False).order_by('-created_at')[:5]

    return render(request, 'edit_banking_info.html', {
        'form': form,
        'employee': employee,
        'notifications': notifications,
        }
    )


@login_required(login_url='/')
def edit_profile_picture(request):
    employee = request.user.employee_user
    
    if request.method == 'POST':
        form = ProfilePictureForm(request.POST, request.FILES, instance=employee)
        if form.is_valid():
            form.save()
            new_picture_url = employee.profile_picture.url
            return JsonResponse({'success': True, 'new_picture_url': new_picture_url})
        else:
            print(form.errors)
            return JsonResponse({'success': False})
    else:
        form = ProfilePictureForm(instance=employee)

    user = request.user
    employee = Employee.objects.get(employee_id=user.employee_id)
    notifications = Notification.objects.filter(recipient=request.user, is_read=False).order_by('-created_at')[:5]

    return render(request, 'profile.html', {'form': form})


@login_required(login_url='/')
def edit_cover_picture(request):
    employee = request.user.employee_user
    
    if request.method == 'POST':
        form = CoverPictureForm(request.POST, request.FILES, instance=employee)
        if form.is_valid():
            form.save()
            new_cover_picture_url = employee.cover_picture.url
            return JsonResponse({'success': True, 'new_cover_picture_url': new_cover_picture_url})
        else:
            return JsonResponse({'success': False})
    else:
        form = CoverPictureForm(instance=employee)

    user = request.user
    employee = Employee.objects.get(employee_id=user.employee_id)
    notifications = Notification.objects.filter(recipient=request.user, is_read=False).order_by('-created_at')[:5]

    return render(request, 'profile.html', {'form': form})


#------------------------------------------------------------- Task Management #

@login_required(login_url='/')
def task_management(request):
    user = request.user
    employee = Employee.objects.get(employee_id=user.employee_id)
    notifications = Notification.objects.filter(recipient=request.user, is_read=False).order_by('-created_at')[:5]
    pending_musters = Muster.objects.filter(status='Pending')
    pending_leave_request = LeaveRequest.objects.filter(status='pending')
    pending_expense = ExpenseClaim.objects.filter(status='pending')
    pending_loan = LoanRequest.objects.filter(status='pending')
    return render(request, 'task_management.html', {
        'employee_id': user.employee_id,
        'employee': employee,
        'notifications': notifications,
        'pending_musters': pending_musters,
        'pending_leave_request': pending_leave_request,
        'pending_expense': pending_expense,
        'pending_loan': pending_loan
        }
    )


def assign_task(request):
    if request.method == 'POST':
        try:
            task_name = request.POST['task_name']
            employee_input = request.POST['employee_emails']
            due_date = request.POST['due_date']

            employee_input_list = [input.strip() for input in employee_input.split(",")]

            users = CustomUser.objects.filter(email__in=employee_input_list) | CustomUser.objects.filter(employee_id__in=employee_input_list)
            
            if users.exists():
                task = Task.objects.create(name=task_name, due_date=due_date, created_by=request.user)
                task.assigned_to.set(users)

                for user in users:
                    notification_message = f"You have been assigned a task: {task_name}, with a due date of {due_date}."
                    Notification.objects.create(recipient=user, message=notification_message)
                
                task.save()
                return JsonResponse({'status': 'success', 'message': 'Task assigned successfully!'})
            else:
                return JsonResponse({'status': 'error', 'message': 'No users found with the provided emails or IDs.'}, status=400)

        except KeyError as e:
            return JsonResponse({'status': 'error', 'message': f'Missing key: {e.args[0]}'}, status=400)
        except Exception as e:
            print(f"Error: {e}")
            return JsonResponse({'status': 'error', 'message': 'An error occurred while assigning the task.'}, status=500)
    
    user = request.user
    employee = Employee.objects.get(employee_id=user.employee_id)
    return render(request, 'task_management.html', {'employee': employee})


@login_required
def tasks_by_date(request):
    if request.method == 'GET':
        date_str = request.GET.get('date')

        date = parse_date(date_str)

        if not date:
            return JsonResponse({'error': 'Invalid date format'}, status=400)

        tasks = Task.objects.filter(due_date=date, assigned_to=request.user)
        
        tasks_data = [
            {
                'id': task.id,
                'name': task.name,
                'due_date': task.due_date,
                'completed': task.completed,
                'assigned_to': [f"{user.first_name} {user.last_name}" for user in task.assigned_to.all()]
            }
            for task in tasks
        ]
        
        return JsonResponse({'tasks': tasks_data})


@csrf_exempt
def mark_task_complete(request, task_id):
    try:
        task = Task.objects.get(id=task_id)
        task.completed = True
        task.save()
        return JsonResponse({'status': 'success', 'message':'Task marked as completed'})
    
    except Task.DoesNotExist:
        return JsonResponse({'status': 'error', 'message': 'Task not found'})


def my_tasks(request):
    try:
        user = request.user

        tasks = Task.objects.filter(assigned_to=user).order_by('-created_at')

        tasks_data = [
            {
                'id': task.id,
                'name': task.name,
                'due_date': task.due_date,
                'completed': task.completed,
                'assigned_to': [f"{user.first_name} {user.last_name}" for user in task.assigned_to.all()]
            }
            for task in tasks
        ]

        return JsonResponse({'tasks': tasks_data})

    except Exception as e:
        print(f"Error: {e}")
        return JsonResponse({'error': str(e)}, status=500)

#------------------------------------------------------------- Expense claim #

@login_required(login_url='/')
def submit_expense_claim(request):
    if request.method == 'POST':
        category = request.POST.get('category')
        date = request.POST.get('date')
        description = request.POST.get('description')
        amount = request.POST.get('amount')
        bill_no = request.POST.get('bill_no')
        receipt = request.FILES.get('receipt')

        expense_claiming = ExpenseClaim.objects.create(
            employee=request.user,
            category=category,
            date=date,
            description=description,
            amount=amount,
            bill_no=bill_no,
            receipt=receipt,
            status='pending'
        )
        return redirect('expense_claims')
    
    return JsonResponse({'success': False, 'error': "Invalid request."})


@login_required(login_url='/')
def expense_claims(request):
    user = request.user
    claims = ExpenseClaim.objects.filter(employee=user)
    employee = Employee.objects.get(employee_id=user.employee_id)
    notifications = Notification.objects.filter(recipient=request.user, is_read=False).order_by('-created_at')[:5]

    return render(request, 'expense_claims.html', {
        'claims': claims,
        'employee': employee,
        'notifications': notifications,
        }
    )


#------------------------------------------------------------- Loan Requests #

@login_required(login_url='/')
def loan_requests(request):
    user = request.user
    loans = LoanRequest.objects.filter(employee=user)
    employee = Employee.objects.get(employee_id=user.employee_id)
    notifications = Notification.objects.filter(recipient=request.user, is_read=False).order_by('-created_at')[:5]

    return render(request, 'loan_requests.html', {
        'loans': loans,
        'employee': employee,
        'notifications': notifications,

        }
    )


@login_required(login_url='/')
def submit_loan_request(request):
    employee = request.user
    if request.method == 'POST':
        loan_type = request.POST.get('loan_type')
        loan_amount = request.POST.get('loan_amount')
        repayment_duration = request.POST.get('repayment_duration')
        interest_rate = request.POST.get('interest_rate')

        loan_request = LoanRequest(
            employee=request.user,
            loan_type=loan_type,
            loan_amount=loan_amount,
            repayment_duration=repayment_duration,
            interest_rate=interest_rate,
            status='pending',
            date_requested=timezone.now()
        )
        notification_message = f"Your Loan request of {loan_type}, amount {loan_amount}, Duration {repayment_duration} with {interest_rate} % has been submitted successfully."
        Notification.objects.create(recipient=loan_request.employee, message=notification_message)
        loan_request.save()

        return redirect('loan_requests')


#------------------------------------------------------------- Reviews-Page #

@login_required(login_url='/')
@staff_member_required
def review_muster(request):
    if not request.user.is_staff:
        return HttpResponseForbidden("You are not authorized to view this page.")
    
    musters = Muster.objects.all()
    if request.method == 'POST':
        muster_id = request.POST.get('muster_id')
        status = request.POST.get('status')
        try:
            muster = Muster.objects.get(id=muster_id)
            muster.status = status
            muster.save()
        except Muster.DoesNotExist:
            pass
        return redirect('staff_notifications')

    musters = Muster.objects.all()
    notifications = Notification.objects.filter(recipient=request.user, is_read=False).order_by('-created_at')[:5]

    return render(request, 'staff_notifications.html', {
        'musters': musters,
        'notifications': notifications,
        }
    )


@login_required(login_url='/')
@staff_member_required
def review_leave(request):
    if not request.user.is_staff:
        return HttpResponseForbidden("You are not authorized to view this page.")
   
    leaves = LeaveRequest.objects.all()
    if request.method == 'POST':
        leave_id = request.POST.get('leave_id')
        status = request.POST.get('status')
        try:
            leave = LeaveRequest.objects.get(id=leave_id)
            leave.status = status
            leave.save()
        except LeaveRequest.DoesNotExist:
            pass
        return redirect('staff_notifications')
   
    leaves = LeaveRequest.objects.all()
    notifications = Notification.objects.filter(recipient=request.user, is_read=False).order_by('-created_at')[:5]

    return render(request, 'staff_notifications.html', {
        'leaves': leaves,
        'notifications': notifications,
        }
    )


@login_required(login_url='/')
@staff_member_required
def review_expense(request):
    if not request.user.is_staff:
        return HttpResponseForbidden("You are not authorized to view this page.")
    
    expenses = ExpenseClaim.objects.all()
    if request.method == 'POST':
        expense_id = request.POST.get('expense_id')
        status = request.POST.get('status')
        try:
            expense = ExpenseClaim.objects.get(id=expense_id)
            expense.status = status
            expense.save()
        except ExpenseClaim.DoesNotExist:
            pass
        return redirect('staff_notifications')

    expenses = ExpenseClaim.objects.all()
    notifications = Notification.objects.filter(recipient=request.user, is_read=False).order_by('-created_at')[:5]

    return render(request, 'staff_notifications.html', {
        'expenses': expenses,
        'notifications': notifications,
        }
    )


@login_required(login_url='/')
@staff_member_required
def review_loan(request):
    if not request.user.is_staff:
        return HttpResponseForbidden("You are not authorized to view this page.")
    
    loans = LoanRequest.objects.all()
    if request.method == 'POST':
        loan_id = request.POST.get('loan_id')
        status = request.POST.get('status')
        try:
            loan = LoanRequest.objects.get(id=loan_id)
            loan.status = status
            loan.save()
        except LoanRequest.DoesNotExist:
            pass
        return redirect('staff_notifications')

    loans = LoanRequest.objects.all()
    notifications = Notification.objects.filter(recipient=request.user, is_read=False).order_by('-created_at')[:5]

    return render(request, 'staff_notifications.html', {
        'loans': loans,
        'notifications': notifications,
        }
    )


#------------------------------------------------------------- Reviews - Notification Bar #

@login_required(login_url='/')
@staff_member_required
def review_muster_notifications(request, muster_id, action):
    muster_request = get_object_or_404(Muster, id=muster_id)

    if action == 'approve':
        muster_request.status = 'approved'
        muster_request.save()
        message = f"Your muster from {muster_request.clock_in_time} to {muster_request.clock_out_time} has been approved."
        Notification.objects.create(recipient=muster_request.user, message=message)

    elif action == 'reject':
        muster_request.status = 'rejected'
        muster_request.save()
        message = f"Your muster from {muster_request.clock_in_time} to {muster_request.clock_out_time} has been rejected."
        Notification.objects.create(recipient=muster_request.user, message=message)

    return redirect('dashboard')

@login_required(login_url='/')
@staff_member_required
def review_leaves_notifications(request, leaves_id, action):
    leave_request = get_object_or_404(LeaveRequest, id=leaves_id)
    leave_balance = Leave.objects.get(employee=leave_request.employee)
 
    if action == 'approve':
        leave_request.status = 'approved'
        leave_request.save()
        message = f"Your Leave request from {leave_request.start_date} to {leave_request.end_date} has been approved."
        Notification.objects.create(recipient=leave_request.employee, message=message)

        requested_leave_days = leave_balance.update_balance(
            leave_request.leave_type,
            leave_request.days_requested,
            leave_request.start_date,
            leave_request.end_date
        )
 
        if requested_leave_days > 0:
            leave_request.days_requested = requested_leave_days
            leave_request.save()
 
    elif action == 'reject':
        leave_request.status = 'rejected'
        leave_request.save()
        message = f"Your Leave request from {leave_request.start_date} to {leave_request.end_date} has been rejected."
        Notification.objects.create(recipient=leave_request.employee, message=message)
 
    return redirect('dashboard')

@login_required(login_url='/')
@staff_member_required
def review_expense_notifications(request, expense_id, action):
    expense_claim = get_object_or_404(ExpenseClaim, id=expense_id)

    if action == 'approve':
        expense_claim.status = 'approved'
        expense_claim.save()
        message = f"Your Expense claim {expense_claim.amount} , {expense_claim.bill_no} has been approved."
        Notification.objects.create(recipient=expense_claim.employee, message=message)

    elif action == 'reject':
        expense_claim.status = 'rejected'
        expense_claim.save()
        message = f"Your Expense claim {expense_claim.amount} , {expense_claim.bill_no} has been rejected."
        Notification.objects.create(recipient=expense_claim.employee, message=message)

    return redirect('dashboard')

@login_required(login_url='/')
@staff_member_required
def review_loan_notifications(request, loan_id, action):
    loan_request = get_object_or_404(LoanRequest, id=loan_id)

    if action == 'approve':
        loan_request.status = 'approved'
        loan_request.save()
        message = f"Your loan request {loan_request.loan_type} to {loan_request.loan_amount} has been approved."
        Notification.objects.create(recipient=loan_request.employee, message=message)

    elif action == 'reject':
        loan_request.status = 'rejected'
        loan_request.save()
        message = f"Your loan request {loan_request.loan_type} to {loan_request.loan_amount} has been rejected."
        Notification.objects.create(recipient=loan_request.employee, message=message)

    return redirect('dashboard')


#------------------------------------------------------------- Reviews-notification bar #

@login_required(login_url='/')
@staff_member_required
def user_list(request):

    employee_id_filter = request.GET.get('employee_id')

    user_query = CustomUser.objects.all()

    if employee_id_filter:
        user_query = user_query.filter(employee_id=employee_id_filter)

    notifications = Notification.objects.filter(recipient=request.user, is_read=False).order_by('-created_at')[:5]
    user = request.user
    employee = Employee.objects.get(employee_id=user.employee_id)

    return render(request, 'user_list.html', {
        'users': user_query,
        'employee': employee,
        'notifications': notifications,
        'employee_id_filter': employee_id_filter,
    })


@login_required(login_url='/')
@staff_member_required
def user_create(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "User created successfully!")
            return redirect('user_list')
    else:
        form = UserCreationForm()
    
    user = request.user
    employee = Employee.objects.get(employee_id=user.employee_id)
    notifications = Notification.objects.filter(recipient=request.user, is_read=False).order_by('-created_at')[:5]

    return render(request, 'user_form.html', {
        'form': form,
        'employee': employee,
        'notifications': notifications,
        }
    )


@login_required(login_url='/')
@staff_member_required
def user_edit(request, pk):
    user = get_object_or_404(CustomUser, pk=pk)
    if request.method == 'POST':
        form = UserCreationForm(request.POST, instance=user)
        if form.is_valid():
            form.save()
            messages.success(request, "User updated successfully!")
            return redirect('user_list')
    else:
        form = UserCreationForm(instance=user)

    user = request.user
    employee = Employee.objects.get(employee_id=user.employee_id)
    notifications = Notification.objects.filter(recipient=request.user, is_read=False).order_by('-created_at')[:5]

    return render(request, 'user_form.html', {
        'form': form,
        'employee': employee,
        'notifications': notifications,
        }
    )


@login_required(login_url='/')
@staff_member_required
def user_confirm_delete(request, pk):
    emp = get_object_or_404(CustomUser, pk=pk)
    
    if request.method == 'POST':
        emp.delete()
        messages.success(request, 'User deleted successfully!')
        return redirect('user_list')

    user = request.user
    current_employee = Employee.objects.get(employee_id=user.employee_id)
    notifications = Notification.objects.filter(recipient=request.user, is_read=False).order_by('-created_at')[:5]
    
    return render(request, 'user_confirm_delete.html', {
        'emp': emp,
        'current_employee': current_employee,
        'notifications': notifications
    })


#------------------------------------------------------------- Policies #

@login_required(login_url='/')
def policy(request):
    user = request.user
    employee = Employee.objects.get(employee_id=user.employee_id)
    notifications = Notification.objects.filter(recipient=request.user, is_read=False).order_by('-created_at')[:5]

    return render(request, 'policy.html' , {
        'employee': employee,
        'notifications': notifications,
        }
    )

@login_required(login_url='/')
def data_retention_policy(request):
    user = request.user
    employee = Employee.objects.get(employee_id=user.employee_id)
    notifications = Notification.objects.filter(recipient=request.user, is_read=False).order_by('-created_at')[:5]

    return render(request, 'data_retention_policy.html' , {
        'employee': employee,
        'notifications': notifications,
        }
    )

@login_required(login_url='/')
def acceptable_use_policy(request):
    user = request.user
    employee = Employee.objects.get(employee_id=user.employee_id)
    notifications = Notification.objects.filter(recipient=request.user, is_read=False).order_by('-created_at')[:5]

    return render(request, 'acceptable_use_policy.html' , {
        'employee': employee,
        'notifications': notifications,
        }
    )

@login_required(login_url='/')
def cookie_policy(request):
    user = request.user
    employee = Employee.objects.get(employee_id=user.employee_id)
    notifications = Notification.objects.filter(recipient=request.user, is_read=False).order_by('-created_at')[:5]

    return render(request, 'cookie_policy.html' , {
        'employee': employee,
        'notifications': notifications,
        }
    )

@login_required(login_url='/')
def refund_cancellation_policy(request):
    user = request.user
    employee = Employee.objects.get(employee_id=user.employee_id)
    notifications = Notification.objects.filter(recipient=request.user, is_read=False).order_by('-created_at')[:5]

    return render(request, 'refund_cancellation_policy.html' , {
        'employee': employee,
        'notifications': notifications,
        }
    )

@login_required(login_url='/')
def terms_of_service(request):
    user = request.user
    employee = Employee.objects.get(employee_id=user.employee_id)
    notifications = Notification.objects.filter(recipient=request.user, is_read=False).order_by('-created_at')[:5]

    return render(request, 'terms_of_service.html' , {
        'employee': employee,
        'notifications': notifications,
        }
    )


#------------------------------------------------------------- Add salaries by Staff #

@login_required(login_url='/')
@staff_member_required
def create_salary(request):
    user = request.user
    employee = None
    
    employee_id_filter = request.GET.get('employee_id', '')
    month_filter = request.GET.get('month', '')

    if month_filter:
        try:
            month_filter = datetime.strptime(month_filter, '%Y-%m')
        except ValueError:
            month_filter = None

    if employee_id_filter:
        employee = Employee.objects.filter(employee_id=employee_id_filter).first()

    if request.method == 'POST':
        form = SalaryForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('salary_list')
    else:
        form = SalaryForm()

    user = request.user
    employee = Employee.objects.get(employee_id=user.employee_id)
    notifications = Notification.objects.filter(recipient=request.user, is_read=False).order_by('-created_at')[:5]

    return render(request, 'create_salary.html', {
        'form': form,
        'employee': employee,
        'notifications': notifications,
        'employee_id_filter': employee_id_filter,
        'month_filter': month_filter,
    })


@login_required(login_url='/')
@staff_member_required
def view_salary(request, salary_id):
    salary = get_object_or_404(Salary, id=salary_id)
    user = request.user
    employee = Employee.objects.get(employee_id=user.employee_id)
    notifications = Notification.objects.filter(recipient=request.user, is_read=False).order_by('-created_at')[:5]
 
    return render(request, 'view_salary.html', {
        'salary': salary,
        'employee': employee,
        'notifications': notifications,
        }
    )


@login_required(login_url='/')
@staff_member_required
def edit_salary(request, salary_id):
    salary = get_object_or_404(Salary, id=salary_id)

    if request.method == 'POST':
        form = SalaryForm(request.POST, instance=salary)
        if form.is_valid():
            form.save()
            return redirect('salary_list')
    else:
        form = SalaryForm(instance=salary)

    user = request.user
    employee = Employee.objects.get(employee_id=user.employee_id)
    notifications = Notification.objects.filter(recipient=request.user, is_read=False).order_by('-created_at')[:5]

    return render(request, 'edit_salary.html', {
        'form': form,
        'employee': employee,
        'notifications': notifications,
        }
    )

@login_required(login_url='/')
@staff_member_required
def delete_salary(request, salary_id):
    salary = get_object_or_404(Salary, id=salary_id)

    if request.method == 'POST':
        salary.delete()
        return redirect('salary_list')
    return render(request, 'delete_salary.html')


@login_required(login_url='/')
@staff_member_required
def salary_list(request):
    employee_id_filter = request.GET.get('employee_id')
    month_filter = request.GET.get('month')

    salary_query = Salary.objects.all()

    if employee_id_filter:
        salary_query = salary_query.filter(employee__employee_id=employee_id_filter)

    if month_filter:
        try:
            month_date = datetime.strptime(month_filter, '%Y-%m')
            salary_query = salary_query.filter(month__year=month_date.year, month__month=month_date.month)
        except ValueError:
            salary_query = salary_query.none()

    user = request.user
    employee = Employee.objects.get(employee_id=user.employee_id)
    notifications = Notification.objects.filter(recipient=request.user, is_read=False).order_by('-created_at')[:5]
    return render(request, 'salary_list.html', {
        'salaries': salary_query,
        'employee': employee,
        'notifications': notifications,
        'employee_id_filter': employee_id_filter,
        'month_filter': month_filter,
    })

#------------------------------------------------------------- Performance #

@login_required(login_url='/')
@staff_member_required
def performance_entry(request):
    user = request.user
    employee = Employee.objects.get(employee_id=user.employee_id)
    notifications = Notification.objects.filter(recipient=request.user, is_read=False).order_by('-created_at')[:5]

    return render(request, 'performance_entry.html', {
        'employee': employee,
        'notifications': notifications
        })
 

@api_view(['POST'])
def submit_performance(request):
    employee_id = request.data.get('employee_id')
    performance_score = request.data.get('performance_score')
 
    if not employee_id or performance_score is None:
        return Response({'error': 'Missing fields'}, status=400)
 
    try:
        employee = Employee.objects.get(employee_id=employee_id)
    except Employee.DoesNotExist:
        return Response({'error': 'Employee not found'}, status=404)
 
    Performance.objects.create(employee=employee, performance_score=performance_score)
    return Response({'message': 'Performance submitted successfully'})
 
 
@api_view(['GET'])
def top_daily_performers(request):
    today = now().date()
    top_performers = Performance.objects.filter(date=today).order_by('-performance_score')[:5]
    serializer = PerformanceSerializer(top_performers, many=True)
    return Response(serializer.data)
 
 
@api_view(['GET'])
def best_monthly_performer(request):
    first_day = now().replace(day=1)
    last_day = first_day + timedelta(days=30)
    top_performer = Performance.objects.filter(date__range=[first_day, last_day]).order_by('-performance_score').first()
    if top_performer:
        serializer = PerformanceSerializer(top_performer)
        return Response(serializer.data)
    return Response({'message': 'No data available'}, status=404)


@login_required(login_url='/')
def performance_page(request):
    performance_data = Performance.objects.select_related('employee').all()
    user = request.user
    employee = Employee.objects.get(employee_id=user.employee_id)
    notifications = Notification.objects.filter(recipient=request.user, is_read=False).order_by('-created_at')[:5]

    return render(request, 'performance_page.html', {
        'performance_data': performance_data,
        'employee': employee,
        'notifications': notifications,
        }
    )


#------------------------------------------------------------- Working days #

@login_required(login_url='/')
@staff_member_required
def working_days(request):
    today = timezone.localtime(timezone.now()).date()

    months = [today]
    for i in range(1, 12):
        previous_month = today.replace(day=1) - timedelta(days=i * 30)
        months.append(previous_month)

    months_formatted = [(month.month, month.year, f"{calendar.month_name[month.month]} {month.year}") for month in months]

    selected_month_year = request.GET.get('month_year', None)
    employee_id_filter = request.GET.get('employee_id', None)
 
    if selected_month_year:
        try:
            selected_month, selected_year = map(int, selected_month_year.split('-'))
            selected_date = timezone.datetime(selected_year, selected_month, 1).date()
        except ValueError:
            raise Http404("Invalid date selection.")
    else:
        selected_date = today
        selected_month, selected_year = selected_date.month, selected_date.year

    period_start = selected_date.replace(day=23)
    if selected_date.day < 23:
        period_start = (selected_date.replace(day=1) - timedelta(days=1)).replace(day=23)
    period_end = (period_start + timedelta(days=32)).replace(day=22)

    if employee_id_filter:
        employees = CustomUser.objects.filter(employee_id=employee_id_filter)
    else:
        employees = CustomUser.objects.all()

    employee_data = []
 
    for employee in employees:
        data = {'employee': employee, 'working_days': [], 'leaves_taken': 0}

        time_entries = TimeEntry.objects.filter(
            user=employee,
            clock_in_time__gte=period_start,
            clock_in_time__lte=period_end,
            clock_out_time__lte=F('clock_in_time') + timedelta(hours=12)
        ).values('clock_in_time__date')
 
        approved_musters = Muster.objects.filter(
            user=employee,
            date__gte=period_start,
            date__lte=period_end,
            status='approved'
        ).values('date')
 
        holidays = Holiday.objects.filter(
            date__gte=period_start,
            date__lte=period_end
        ).values('date')
 
        approved_leaves = LeaveRequest.objects.filter(
            employee=employee,
            start_date__gte=period_start,
            end_date__lte=period_end,
            status='approved'
        ).values('leave_type', 'start_date', 'end_date', 'days_requested')

        total_leave_days = 18
        remaining_leave_days = total_leave_days

        combined_dates = set(time_entries.values_list('clock_in_time__date', flat=True)) | \
                          set(approved_musters.values_list('date', flat=True)) | \
                          set(holidays.values_list('date', flat=True))

        total_working_days = 0
        counted_days = set()

        leaves_taken = set()
 
        for leave in approved_leaves:
            leave_days = leave['days_requested']

            if remaining_leave_days > 0:
                if leave_days <= remaining_leave_days:
                    remaining_leave_days -= leave_days
                    total_working_days += leave_days 
                    leave_day = leave['start_date']
                    for i in range(leave_days):
                        current_leave_day = leave_day + timedelta(days=i)
                        leaves_taken.add(current_leave_day)

        standardized_dates = set()
        for date in combined_dates:
            if isinstance(date, datetime):
                standardized_dates.add(date.date())
            else:
                standardized_dates.add(date)

        working_dates = {date for date in standardized_dates if date.weekday() < 5}

        for date in working_dates:
            if date not in counted_days:
                total_working_days += 1
                counted_days.add(date)

        data['leaves_taken'] = len(leaves_taken) 
        data['working_days'].append({
            'period_label': f"{period_start.strftime('%b %Y')} - {period_end.strftime('%b %Y')}",
            'working_days': total_working_days,
        })
        data['remaining_leave_days'] = remaining_leave_days
 
        employee_data.append(data)
 
    user = request.user
    employee = Employee.objects.get(employee_id=user.employee_id)
    notifications = Notification.objects.filter(recipient=request.user, is_read=False).order_by('-created_at')[:5]

    return render(request, 'working_days.html', {
        'employee_data': employee_data,
        'months': months_formatted,
        'selected_month': selected_month,
        'selected_year': selected_year,
        'employee_id_filter': employee_id_filter,
        'employee': employee,
        'notifications': notifications,
    })


#------------------------------------------------------------- Company adding by staff #

@login_required(login_url='/')
@staff_member_required
def company_list(request):
    companies = Company_check.objects.all()
    user = request.user
    employee = Employee.objects.get(employee_id=user.employee_id)
    notifications = Notification.objects.filter(recipient=request.user, is_read=False).order_by('-created_at')[:5]
    return render(request, 'company_list.html', {'companies': companies,'employee': employee,'notifications': notifications})

@login_required(login_url='/')
@staff_member_required
def company_create(request):
    if request.method == 'POST':
        form = Company_checkForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('company_list')
    else:
        form = Company_checkForm()
    
    user = request.user
    employee = Employee.objects.get(employee_id=user.employee_id)
    notifications = Notification.objects.filter(recipient=request.user, is_read=False).order_by('-created_at')[:5]
    return render(request, 'company_form.html', {'form': form,'employee': employee,'notifications': notifications})

@login_required(login_url='/')
@staff_member_required
def company_edit(request, pk):
    company = get_object_or_404(Company_check, pk=pk)
    if request.method == 'POST':
        form = Company_checkForm(request.POST, instance=company)
        if form.is_valid():
            form.save()
            return redirect('company_list')
    else:
        form = Company_checkForm(instance=company)
    
    user = request.user
    employee = Employee.objects.get(employee_id=user.employee_id)
    notifications = Notification.objects.filter(recipient=request.user, is_read=False).order_by('-created_at')[:5]
    return render(request, 'company_form.html', {'form': form,'employee': employee,'notifications': notifications})

@login_required(login_url='/')
@staff_member_required
def company_delete(request, pk):
    company = get_object_or_404(Company_check, pk=pk)
    if request.method == 'POST':
        company.delete()
        return redirect('company_list')
    user = request.user
    employee = Employee.objects.get(employee_id=user.employee_id)
    notifications = Notification.objects.filter(recipient=request.user, is_read=False).order_by('-created_at')[:5]
    return render(request, 'company_delete.html', {'company': company,'employee': employee,'notifications': notifications})


#------------------------------------------------------------- Task list by staff #

@login_required(login_url='/')
@staff_member_required
def task_list(request):
    tasks = Task.objects.all()
    employee_id = request.GET.get('employee_id', '')
    month = request.GET.get('month', '')

    if employee_id:

        try:
            employee = CustomUser.objects.get(employee_id=employee_id)
            tasks = tasks.filter(assigned_to=employee)

        except CustomUser.DoesNotExist:
            tasks = tasks.none()

    if month:
        try:
            month_start = datetime.strptime(month, '%Y-%m').date()
            month_end = month_start.replace(day=28) + timedelta(days=4)
            month_end = month_end.replace(day=1) - timedelta(days=1)
            tasks = tasks.filter(due_date__range=[month_start, month_end])
        except ValueError:
            pass

    months = [
        {'num': f"{i:02d}", 'name': datetime(2025, i, 1).strftime('%B')}
        for i in range(1, 13)
    ]

    user = request.user
    employee = Employee.objects.get(employee_id=user.employee_id)
    notifications = Notification.objects.filter(recipient=request.user, is_read=False).order_by('-created_at')[:5]
    return render(request, 'task_list.html', {
        'tasks': tasks,
        'months': months,
        'employee': employee,
        'notifications': notifications,
        'current_month': datetime.now().strftime('%Y-%m')
    })


#------------------------------------------------------------- Company adding by staff #

@login_required(login_url='/')
@staff_member_required
def performance_list(request):
    today = timezone.now().date()
    first_day_of_month = today.replace(day=1)
    last_day_of_month = first_day_of_month + timedelta(days=31)
    last_day_of_month = last_day_of_month.replace(day=1) - timedelta(days=1)

    performance_data = Performance.objects.filter(date__range=[first_day_of_month, last_day_of_month])

    employee_id = request.GET.get('employee_id')
    month = request.GET.get('month')
 
    if employee_id:
        performance_data = performance_data.filter(employee__employee_id=employee_id)
 
    if month:
        month_start = timezone.datetime.strptime(month, '%Y-%m').date()
        month_end = month_start.replace(day=28) + timedelta(days=4)
        performance_data = performance_data.filter(date__range=[month_start, month_end])

    employees = Employee.objects.all()

    months = [(timezone.datetime(today.year, m, 1).strftime('%Y-%m'), timezone.datetime(today.year, m, 1).strftime('%B')) for m in range(1, 13)]
 
    user = request.user
    employee = Employee.objects.get(employee_id=user.employee_id)
    notifications = Notification.objects.filter(recipient=request.user, is_read=False).order_by('-created_at')[:5]
    return render(request, 'performance_list.html', {
        'performance_data': performance_data,
        'employees': employees,
        'current_month': today.month,
        'current_year': today.year,
        'months': months,
        'employee': employee,
        'notifications': notifications
    })


#------------------------------------------------------------- Company adding by staff #

@login_required(login_url='/')
@staff_member_required
def employee_list(request):
    employee_id_filter = request.GET.get('employee_id')
    employee_query = Employee.objects.all()

    if employee_id_filter:
        employee_query = employee_query.filter(employee_id=employee_id_filter)

    notifications = Notification.objects.filter(recipient=request.user, is_read=False).order_by('-created_at')[:5]
    user = request.user
    employee = Employee.objects.get(employee_id=user.employee_id)
    return render(request, 'employee_list.html', {
        'employee_query': employee_query,
        'employee': employee,
        'notifications': notifications,
        'employee_id_filter': employee_id_filter,
    })


# @login_required(login_url='/')
# @staff_member_required
# def employee_create(request):
#     if request.method == 'POST':
#         form = EmployeeProfileForm(request.POST, request.FILES)
#         if form.is_valid():
#             form.save()
#             messages.success(request, 'Employee added successfully!')
#             return redirect('employee_list')
#     else:
#         form = EmployeeProfileForm()
#     user = request.user
#     employee = Employee.objects.get(employee_id=user.employee_id)
#     notifications = Notification.objects.filter(recipient=request.user, is_read=False).order_by('-created_at')[:5]
#     return render(request, 'employee_create.html', {'form': form,'employee': employee,'notifications': notifications})

@login_required(login_url='/')
@staff_member_required
def employee_create(request):
    if request.method == 'POST':
        form = EmployeeProfileForm(request.POST, request.FILES)
        # Validate if the form is valid
        if form.is_valid():
            # Check if a CustomUser exists with the provided employee_id
            employee_id = form.cleaned_data['employee_id']
            try:
                # Check if the CustomUser exists with the given employee_id
                user = CustomUser.objects.get(employee_id=employee_id)
                # If found, create an Employee for this CustomUser
                employee = form.save(commit=False)
                employee.user = user  # Link the user to the employee
                employee.save()  # Save the employee
                messages.success(request, 'Employee added successfully!')
                return redirect('employee_list')
            except CustomUser.DoesNotExist:
                # If no user exists with that employee_id, show an error message
                messages.error(request, 'No user found with the provided employee ID.')
    else:
        form = EmployeeProfileForm()

    return render(request, 'employee_create.html', {'form': form})



@login_required(login_url='/')
@staff_member_required
def employee_edit(request, pk):
    employee = get_object_or_404(Employee, pk=pk)
    if request.method == 'POST':
        form = EmployeeProfileForm(request.POST, request.FILES, instance=employee)
        if form.is_valid():
            form.save()
            messages.success(request, 'Employee updated successfully!')
            return redirect('employee_list')
    else:
        form = EmployeeProfileForm(instance=employee)

    user = request.user
    employee = Employee.objects.get(employee_id=user.employee_id)
    notifications = Notification.objects.filter(recipient=request.user, is_read=False).order_by('-created_at')[:5]
    return render(request, 'employee_create.html', {'form': form, 'employee': employee,'notifications': notifications})


@login_required(login_url='/')
@staff_member_required
def employee_delete(request, pk):
    employee = get_object_or_404(Employee, pk=pk)
    
    if request.method == 'POST':
        employee.delete()
        messages.success(request, 'Employee deleted successfully!')
        return redirect('employee_list')

    user = request.user
    current_employee = Employee.objects.get(employee_id=user.employee_id)
    notifications = Notification.objects.filter(recipient=request.user, is_read=False).order_by('-created_at')[:5]
    
    return render(request, 'employee_delete.html', {
        'employee': employee,
        'current_employee': current_employee,
        'notifications': notifications
    })



#------------------------------------------------------------- Holidays adding by staff #

@login_required(login_url='/')
@staff_member_required
def holidays_list(request):
    holidays = Holiday.objects.all().order_by('date')
    user = request.user
    employee = Employee.objects.get(employee_id=user.employee_id)
    notifications = Notification.objects.filter(recipient=request.user, is_read=False).order_by('-created_at')[:5]
    return render(request, 'holidays_list.html', {'holidays': holidays, 'employee': employee, 'notifications': notifications})

@login_required(login_url='/')
@staff_member_required
def holiday_create(request):
    if request.method == 'POST':
        form = HolidaysForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('holidays_list')
    else:
        form = HolidaysForm()
    
    user = request.user
    employee = Employee.objects.get(employee_id=user.employee_id)
    notifications = Notification.objects.filter(recipient=request.user, is_read=False).order_by('-created_at')[:5]
    return render(request, 'holiday_form.html', {'form': form,'employee': employee,'notifications': notifications})

@login_required(login_url='/')
@staff_member_required
def holiday_view(request, pk):
    holiday = get_object_or_404(Holiday, pk=pk)
    user = request.user
    employee = Employee.objects.get(employee_id=user.employee_id)
    notifications = Notification.objects.filter(recipient=request.user, is_read=False).order_by('-created_at')[:5]
    return render(request, 'holiday_view.html', {'holiday': holiday,'employee': employee,'notifications': notifications})

@login_required(login_url='/')
@staff_member_required
def holiday_edit(request, pk):
    holiday = get_object_or_404(Holiday, pk=pk)
    if request.method == 'POST':
        form = HolidaysForm(request.POST, instance=holiday)
        if form.is_valid():
            form.save()
            return redirect('holiday_view', pk=holiday.pk)
    else:
        form = HolidaysForm(instance=holiday)
    
    user = request.user
    employee = Employee.objects.get(employee_id=user.employee_id)
    notifications = Notification.objects.filter(recipient=request.user, is_read=False).order_by('-created_at')[:5]
    return render(request, 'holiday_form.html', {'form': form,'employee': employee,'notifications': notifications})

@login_required(login_url='/')
@staff_member_required
def holiday_delete(request, pk):
    holiday = get_object_or_404(Holiday, pk=pk)
    if request.method == 'POST':
        holiday.delete()
        return redirect('holidays_list')
    
    user = request.user
    employee = Employee.objects.get(employee_id=user.employee_id)
    notifications = Notification.objects.filter(recipient=request.user, is_read=False).order_by('-created_at')[:5]
    return render(request, 'holiday_delete.html', {'holiday': holiday,'employee': employee,'notifications': notifications})


#------------------------------------------------------------- Leave balance adding by staff #

@login_required(login_url='/')
@staff_member_required
def leave_list(request):
    employee_id_filter = request.GET.get('employee_id')

    leave_query = Leave.objects.all()

    if employee_id_filter:
        leave_query = leave_query.filter(employee__employee_id=employee_id_filter)

    notifications = Notification.objects.filter(recipient=request.user, is_read=False).order_by('-created_at')[:5]

    user = request.user
    employee = Employee.objects.get(employee_id=user.employee_id)

    return render(request, 'leave_list.html', {
        'leaves': leave_query,
        'employee': employee,
        'notifications': notifications,
        'employee_id_filter': employee_id_filter,
    })


@login_required(login_url='/')
@staff_member_required
def leave_create(request):
    if request.method == 'POST':
        form = LeaveForm(request.POST)
        if form.is_valid():
            employee_id = form.cleaned_data['employee_id']
            
            try:
                employee = CustomUser.objects.get(employee_id=employee_id)
                leave_balance, created = Leave.objects.get_or_create(employee=employee)
                leave_balance.advance_privilege_leave = form.cleaned_data.get('advance_privilege_leave', leave_balance.advance_privilege_leave)
                leave_balance.sick_leave = form.cleaned_data.get('sick_leave', leave_balance.sick_leave)
                leave_balance.casual_leave = form.cleaned_data.get('casual_leave', leave_balance.casual_leave)
                leave_balance.save()
                return redirect('leave_list')

            except CustomUser.DoesNotExist:
                return JsonResponse({'status': 'error', 'message': 'Employee with the given ID does not exist.'}, status=400)
        else:
            return JsonResponse({'status': 'error', 'message': 'Invalid form submission.'}, status=400)
    else:
        form = LeaveForm()
    
    user = request.user
    employee = Employee.objects.get(employee_id=user.employee_id)
    notifications = Notification.objects.filter(recipient=request.user, is_read=False).order_by('-created_at')[:5]
    
    return render(request, 'leave_create.html', {'form': form, 'employee': employee, 'notifications': notifications})


@login_required(login_url='/')
@staff_member_required
def leave_detail(request, pk):
    leave = get_object_or_404(Leave, pk=pk)
    user = request.user
    employee = Employee.objects.get(employee_id=user.employee_id)
    notifications = Notification.objects.filter(recipient=request.user, is_read=False).order_by('-created_at')[:5]
    return render(request, 'leave_detail.html', {'leave': leave,'employee': employee,'notifications': notifications})


@login_required(login_url='/')
@staff_member_required
def leave_edit(request, pk):
    leave = get_object_or_404(Leave, pk=pk)
    if request.method == 'POST':
        form = LeaveForm(request.POST, instance=leave)
        if form.is_valid():
            form.save()
            return redirect('leave_list')
    else:
        form = LeaveForm(instance=leave)

    user = request.user
    employee = Employee.objects.get(employee_id=user.employee_id)
    notifications = Notification.objects.filter(recipient=request.user, is_read=False).order_by('-created_at')[:5]
    return render(request, 'leave_edit.html', {'form': form,'employee': employee,'notifications': notifications})


@login_required(login_url='/')
@staff_member_required
def leave_delete(request, pk):
    leave = get_object_or_404(Leave, pk=pk)
    if request.method == "POST":
        leave.delete()
        return redirect('leave_list')
    
    user = request.user
    employee = Employee.objects.get(employee_id=user.employee_id)
    notifications = Notification.objects.filter(recipient=request.user, is_read=False).order_by('-created_at')[:5]
    return render(request, 'leave_delete.html', {'leave': leave,'employee': employee,'notifications': notifications})
