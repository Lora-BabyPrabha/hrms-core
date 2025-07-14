from django.db import models
from django.core.validators import RegexValidator
from datetime import timedelta
from django.utils import timezone
import datetime
from django.contrib.auth.models import AbstractUser
from app.manager import UserManager
from django.db.models import ImageField
from django.core.validators import RegexValidator
from django.contrib.auth.models import AbstractUser
from .validators import StrongPasswordValidator
from django.core.exceptions import ValidationError
from django.db import models


# Create your models here.

ROLE_TYPE = (
    ('Manager',"Manager"),
    ('HR',"HR"),
    ('Employee',"Employee")
)

class CustomUser(AbstractUser):
    username = None
    name = models.CharField(max_length=150)  #!-- Added-->
    role = models.CharField(choices=ROLE_TYPE, max_length=100, error_messages={'required': "Role must be provided"})
    employee_id = models.CharField(max_length=100, unique=True)
    email = models.EmailField(max_length=254, unique=True)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

    USERNAME_FIELD = "employee_id"
    REQUIRED_FIELDS = ['email']

    def __unicode__(self):
        return self.employee_id
        
    def save(self, *args, **kwargs): #Added
        if self.name == 'Unknown' or not self.name:
            full_name = f"{self.first_name} {self.last_name}".strip()
            if full_name:
                self.name = full_name
            else:
                self.name = self.email.split('@')[0]
        super().save(*args, **kwargs)

    objects = UserManager()


#------------------------------------------------------------- Notifications #

class Notification(models.Model):
    recipient = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    message = models.TextField()
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def _str_(self):
        return f"Notification for {self.recipient.employee_id}: {self.message[:5]}"
        

#------------------------------------------------------------- Company check #

class Company_check(models.Model):
    company_name  = models.CharField(max_length=500, null=True, blank=True)
     
    def __str__(self):
        return self.company_name
    

#------------------------------------------------------------- Holidays #

class Holiday(models.Model):
    name  = models.CharField(max_length=500, null=True, blank=True)
    day  = models.CharField(max_length=500, null=True, blank=True)
    date = models.DateField(null=True,blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)
     
    def __str__(self):
        return self.name
    

#------------------------------------------------------------- Employee details #

class Employee(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE, related_name='employee_user', null=True, blank=True)
    employee_id = models.CharField(max_length=20, unique=True, blank=True, null=True)
    name = models.CharField(max_length=100)
    designation = models.CharField(max_length=50)
    department = models.CharField(max_length=50)
    uan_number = models.CharField(max_length=20, unique=True)
    pan_number = models.CharField(max_length=20, unique=True)
    pf_number=models.CharField(max_length=30,blank=True,null=True)
    date_of_birth = models.DateField(null=True, blank=True)
    gender = models.CharField(max_length=10, choices=[('Male', 'Male'), ('Female', 'Female'), ('Other', 'Other')], null=True, blank=True)
    nationality = models.CharField(max_length=50, null=True, blank=True)
    address=models.CharField(max_length=30, null=True, blank=True)
    phone_number = models.CharField(max_length=15, validators=[RegexValidator(regex=r'^\+?\d{10,15}$')], null=True, blank=True)
    reporting_manager = models.CharField(max_length=100, null=True, blank=True)
    employee_type = models.CharField(max_length=20, choices=[('Full-time', 'Full-time'), ('Part-time', 'Part-time'), ('Contract', 'Contract')], null=True, blank=True)
    work_location = models.CharField(max_length=20, choices=[('On-site', 'On-site'), ('Remote', 'Remote'), ('Hybrid', 'Hybrid')], null=True, blank=True)
    bank_account_number = models.CharField(max_length=20, null=True, blank=True)
    bank_name = models.CharField(max_length=100, null=True, blank=True)
    ifsc_code = models.CharField(max_length=11, null=True, blank=True)
    aadhar_number = models.CharField(max_length=12, unique=True, null=True, blank=True)
    profile_picture = ImageField(upload_to='profile_pictures/', null=True, blank=True, default='profile_pictures/default_profile.jpg')
    cover_picture = ImageField(upload_to='cover_pictures/', null=True, blank=True, default='cover_pictures/default_cover.jpg')
    

    def save(self, *args, **kwargs):
        if not self.employee_id and self.user:
            self.employee_id = self.user.employee_id
        super(Employee, self).save(*args, **kwargs)

    def __str__(self):
        return self.name
    

#------------------------------------------------------------- Salary #
 
class Salary(models.Model):
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE)
    month = models.DateField()
    current_month_calculated_days=models.IntegerField(blank=True,null=True)
    current_month_paid_days=models.IntegerField(blank=True,null=True)
    basic_salary = models.DecimalField(max_digits=10, decimal_places=2)
    house_rent_allowance = models.DecimalField(max_digits=10, decimal_places=2, default=0.0)
    special_allowance=models.DecimalField(max_digits=10, decimal_places=2, default=0.0)
    conveyance_allowance=models.DecimalField(max_digits=10, decimal_places=2, default=0.0)
    total_fixed_salary = models.DecimalField(max_digits=10, decimal_places=2, default=0.0, blank=True, null=True)
 
 
    pf_contribution = models.DecimalField(max_digits=10, decimal_places=2, default=0.0)
    professional_tax=models.DecimalField(max_digits=10, decimal_places=2, default=0.0,null=True,blank=True)
    income_tax=models.DecimalField(max_digits=10, decimal_places=2, default=0.0,null=True,blank=True)
 
    performance_bonus=models.DecimalField(max_digits=10, decimal_places=2, default=0.0,null=True,blank=True)
    other_incentives=models.DecimalField(max_digits=10, decimal_places=2, default=0.0,null=True,blank=True)
 
    medical_insurance=models.DecimalField(max_digits=10, decimal_places=2, default=0.0,null=True,blank=True)
    stationery_misc = models.DecimalField(max_digits=10, decimal_places=2, default=0.0, blank=True, null=True)
    deductions = models.DecimalField(max_digits=10, decimal_places=2, default=0.0, blank=True, null=True)
    gross_salary = models.DecimalField(max_digits=10, decimal_places=2, default=0.0, blank=True, null=True)
    net_salary = models.DecimalField(max_digits=10, decimal_places=2, default=0.0, blank=True, null=True)
    total_variable_pay= models.DecimalField(max_digits=10, decimal_places=2, default=0.0, blank=True, null=True)
    per_day_salary=models.DecimalField(max_digits=10, decimal_places=2, default=0.0, blank=True, null=True)
    actual_salary=models.DecimalField(max_digits=10, decimal_places=2, default=0.0, blank=True, null=True)
    loan_deductions=models.DecimalField(max_digits=10, decimal_places=2, default=0.0, blank=True, null=True)
 
    def save(self, *args, **kwargs):
        self.total_fixed_salary=self.basic_salary+self.house_rent_allowance+self.special_allowance+self.conveyance_allowance
        self.deductions=self.pf_contribution+self.professional_tax+self.medical_insurance+self.stationery_misc+self.income_tax
        self.total_variable_pay=self.performance_bonus+self.other_incentives
        self.gross_salary=self.total_fixed_salary+ self.deductions
        self.net_salary = self.total_fixed_salary-self.total_variable_pay
        self.per_day_salary=self.net_salary/self.current_month_calculated_days
        self.actual_salary=self.per_day_salary*self.current_month_paid_days
 
        super(Salary, self).save(*args, **kwargs)
 
    def __str__(self):
        return f"{self.employee.employee_id} - {self.month.strftime('%B %Y')}"


#------------------------------------------------------------- Time Entry #

class TimeEntry(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    clock_in_time = models.DateTimeField(null=True, blank=True)
    clock_out_time = models.DateTimeField(null=True, blank=True)
    clock_in_latitude = models.FloatField(null=True, blank=True)
    clock_in_longitude = models.FloatField(null=True, blank=True)
    clock_out_latitude = models.FloatField(null=True, blank=True)
    clock_out_longitude = models.FloatField(null=True, blank=True)

    def __str__(self):
        return f"{self.user.employee_id} - Clock In: {self.clock_in_time} - Clock Out: {self.clock_out_time}"
    

#------------------------------------------------------------- Muster check-in/check-out #

REASON_TYPE = (
    ('On-site',"On-site"),
    ('Forgot Login/out',"Forgot Login/out"),
    ('Forgot Logout',"Forgot Logout"),
    ('Network Issue',"Network Issue"),
    ('Work From Home',"Work From Home"),
)

class Muster(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    employee_id = models.CharField(max_length=100)
    date = models.DateTimeField()
    clock_in_time = models.DateTimeField(auto_now=False, auto_now_add=False)
    clock_out_time = models.DateTimeField(auto_now=False, auto_now_add=False)
    reason = models.CharField(choices=REASON_TYPE, max_length=150, blank=True, null=True)
    notes = models.CharField(max_length=500, blank=True, null=True)
    status = models.CharField(max_length=10, choices=[('pending', 'Pending'), ('approved', 'Approved'), ('rejected', 'Rejected')], default='pending')
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"Leave Application by {self.employee_id} - {self.reason} on {self.date.strftime('%d-%m-%Y')}"


#------------------------------------------------------------- Leave and Balance #

class Leave(models.Model):
    employee = models.OneToOneField('CustomUser', on_delete=models.CASCADE)
    advance_privilege_leave = models.IntegerField(default=6)
    sick_leave = models.IntegerField(default=6)
    casual_leave = models.IntegerField(default=6)
 
    def __str__(self):
        return f"{self.employee.employee_id} Leave Balance"
   
    def update_balance(self, leave_type, days_requested, start_date, end_date):
        # Check if the leave type is valid and balance is enough
        weekdays_requested = 0
        current_day = start_date
        while current_day <= end_date:
            if current_day.weekday() < 5:  # Only count weekdays (Mon-Fri)
                weekdays_requested += 1
            current_day += timedelta(days=1)
 
        # Deduct leave balance based on weekdays requested, not weekends
        if leave_type == 'advance_privilege':
            if self.advance_privilege_leave >= weekdays_requested:
                self.advance_privilege_leave -= weekdays_requested
            else:
                weekdays_requested = self.advance_privilege_leave
                self.advance_privilege_leave = 0  # Prevent going negative
        elif leave_type == 'sick':
            if self.sick_leave >= weekdays_requested:
                self.sick_leave -= weekdays_requested
            else:
                weekdays_requested = self.sick_leave
                self.sick_leave = 0  # Prevent going negative
        elif leave_type == 'casual':
            if self.casual_leave >= weekdays_requested:
                self.casual_leave -= weekdays_requested
            else:
                weekdays_requested = self.casual_leave
                self.casual_leave = 0  # Prevent going negative
 
        self.save()
        # If there's only 1 day left in the balance, count it as a working day
        if weekdays_requested == 1:
            return 1
        return weekdays_requested
 
 
class LeaveRequest(models.Model):
    LEAVE_CHOICES = [
        ('advance_privilege', 'Advance Privilege Leave'),
        ('sick', 'Sick Leave'),
        ('casual', 'Casual Leave'),
        # ('regular', 'Regular Leave'),
    ]
   
    employee = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    leave_type = models.CharField(max_length=20, choices=LEAVE_CHOICES)
    start_date = models.DateField()
    end_date = models.DateField()
    reason = models.TextField()
    days_requested = models.PositiveIntegerField()
    status = models.CharField(max_length=10, choices=[('pending', 'Pending'), ('approved', 'Approved'), ('rejected', 'Rejected')], default='pending')
    created_at = models.DateTimeField(auto_now_add=True)
 
    def __str__(self):
        return f"Leave request for {self.employee.employee_id} ({self.leave_type})"
 

#------------------------------------------------------------- Leave and Balance #

class ExpenseClaim(models.Model):
    CATEGORY_CHOICES = [
        ('Travel Expense', 'Travel Expense'),
        ('Food Expense', 'Food Expense'),
        ('Accommodation', 'Accommodation'),
        ('Team Lunch', 'Team Lunch'),
        ('Other','Other')
    ]

    employee = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    category = models.CharField(max_length=50, choices=CATEGORY_CHOICES)
    date = models.DateField()
    description = models.TextField()
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    bill_no = models.CharField(max_length=50, blank=True, null=True)
    receipt = models.FileField(upload_to='expense_receipts/')
    status = models.CharField(max_length=10, choices=[('pending', 'Pending'), ('approved', 'Approved'), ('rejected', 'Rejected')], default='pending')

    def __str__(self):
        return f"{self.employee} - {self.category} - {self.date}"
    

#------------------------------------------------------------- Leave and Balance #

class LoanRequest(models.Model):
    LOAN_TYPE_CHOICES = [
        ('Personal Loan', 'Personal Loan'),
        ('Home Loan', 'Home Loan'),
        ('Education Loan', 'Education Loan')
    ]

    employee = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    loan_type = models.CharField(max_length=50, choices=LOAN_TYPE_CHOICES)
    loan_amount = models.DecimalField(max_digits=10, decimal_places=2)
    repayment_duration = models.IntegerField()
    interest_rate = models.DecimalField(max_digits=5, decimal_places=2)
    status = models.CharField(max_length=10, choices=[('pending', 'Pending'), ('approved', 'Approved'), ('rejected', 'Rejected')], default='pending')
    date_requested = models.DateTimeField(auto_now_add=True)
    date = models.DateField(auto_now_add=True)


    def __str__(self):
        return f"{self.employee.employee_id} - {self.loan_type} ({self.status})"
    
    def get_approve_url(self):
        return f"/loan-requests/approve/{self.id}/"
    
    def get_reject_url(self):
        return f"/loan-requests/reject/{self.id}/"
    

#------------------------------------------------------------- Task management #

from django.contrib.auth import get_user_model
CustomUser = get_user_model()


# class Task(models.Model):
#     name = models.CharField(max_length=255, default='No Task Name')
#     assigned_to = models.ManyToManyField(CustomUser,related_name="tasks")
#     due_date = models.DateField()
#     completed = models.BooleanField(default=False)
#     created_at = models.DateTimeField(default=timezone.now)

#     def _str_(self):
#         return self.task_name

#     class Meta:
#         ordering = ['due_date']


class Task(models.Model):
    name = models.CharField(max_length=255, default='No Task Name')
    assigned_to = models.ManyToManyField(CustomUser,related_name="tasks")
    due_date = models.DateField()
    completed = models.BooleanField(default=False)
    created_at = models.DateTimeField(default=timezone.now)
    created_by = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name="tasks_created", null=True)  # Added this line


    def _str_(self):
        return self.task_name

    class Meta:
        ordering = ['due_date']

#------------------------------------------------------------- Performance #

class Performance(models.Model):
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE)
    performance_score = models.IntegerField()
    date = models.DateField(auto_now_add=True)
 
    class Meta:
        ordering = ['-date']
