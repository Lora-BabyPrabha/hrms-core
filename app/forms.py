from django import forms
from app.models import *
from app.forms import *
from django.contrib.auth.models import *
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from app.models import CustomUser
from django.contrib.auth.forms import PasswordChangeForm
import re
from django.core.exceptions import ValidationError


class ResetPasswordForm(forms.Form):
    employee_id = forms.CharField(label="Employee ID", max_length=50)
    old_password = forms.CharField(label="Old Password", widget=forms.PasswordInput)
    new_password = forms.CharField(label="New Password", widget=forms.PasswordInput)
    confirm_password = forms.CharField(label="Confirm Password", widget=forms.PasswordInput)
 
    def clean(self):
        cleaned_data = super().clean()
        new_password = cleaned_data.get('new_password')
        confirm_password = cleaned_data.get('confirm_password')
 
        # Check if the new password and confirm password match
        if new_password != confirm_password:
            self.add_error('confirm_password', "The new password and confirm password do not match.")
       
        # Check for strong password requirements
        self.validate_password_strength(new_password)
 
        return cleaned_data
 
    def validate_password_strength(self, password):
        """
        Validates that the password meets the required strength criteria:
        - At least 8 characters
        - At least 1 uppercase letter
        - At least 1 special character
        - At least 1 number
        """
        errors = []
 
        # Check password length
        if len(password) < 8:
            errors.append("Password must be at least 8 characters long.")
 
        # Check for at least 1 uppercase letter
        if not re.search(r'[A-Z]', password):
            errors.append("Password must contain at least one uppercase letter.")
 
        # Check for at least 1 special character
        if not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):  # Special characters
            errors.append("Password must contain at least one special character.")
 
        # Check for at least 1 number
        if not re.search(r'[0-9]', password):
            errors.append("Password must contain at least one number.")
 
        # If there are any errors, combine them into one message
        if errors:
            # Combine all errors into a single string with line breaks
            error_message = " ".join(errors)
            self.add_error('new_password', error_message)
 


class ForgotPasswordForm(forms.Form):
    email = forms.EmailField(label="Email", max_length=100)
    

# class ResetPasswordWithOTPForm(forms.Form):
#     email = forms.EmailField(label="Email")
#     otp = forms.CharField(label="OTP", max_length=6)
#     new_password = forms.CharField(label="New Password", widget=forms.PasswordInput)
#     confirm_password = forms.CharField(label="Confirm Password", widget=forms.PasswordInput)

#     def clean(self):
#         cleaned_data = super().clean()
#         new_password = cleaned_data.get('new_password')
#         confirm_password = cleaned_data.get('confirm_password')

#         if new_password != confirm_password:
#             raise forms.ValidationError("The new password and confirm password do not match.")
#         return cleaned_data
    
    
# class UserCreationForm(forms.ModelForm):
#     class Meta:
#         model = CustomUser
#         fields = '__all__'

#     def save(self, commit=True):
#         user = super(UserCreationForm, self).save(commit=False)
#         user.set_password(self.cleaned_data["password"])
#         if commit:
#             user.save()
#         return user

from django import forms
from django.core.exceptions import ValidationError
import re
from .models import CustomUser  # Make sure to import CustomUser model

class UserCreationForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput)

    class Meta:
        model = CustomUser
        fields = '__all__'
        
    def clean_password(self):
        password = self.cleaned_data.get("password")
        user = self.instance

        # Enforce password validation
        self.validate_password_strength(password, user)
        
        return password

    def validate_password_strength(self, password, user):
        # Check minimum length
        if len(password) < 8:
            raise ValidationError("Password must be at least 8 characters long.")
        
        # Check for at least one uppercase letter
        if not any(char.isupper() for char in password):
            raise ValidationError("Password must contain at least one uppercase letter.")
        
        # Check for at least one lowercase letter
        if not any(char.islower() for char in password):
            raise ValidationError("Password must contain at least one lowercase letter.")
        
        # Check for special characters
        if not re.search(r'[@#$%^&+=]', password):
            raise ValidationError("Password must contain at least one special character (e.g., @, #, $, %, ^, &, +).")
        
        # Check that the password does not contain the username or employee ID
        if user.username and user.username in password:
            raise ValidationError("Password cannot contain your username.")
        if user.employee_id and user.employee_id in password:
            raise ValidationError("Password cannot contain your employee ID.")

    def save(self, commit=True):
        user = super(UserCreationForm, self).save(commit=False)
        password = self.cleaned_data["password"]
        user.set_password(password)  # Set the password after validation
        if commit:
            user.save()
        return user



# forms.py (frontend form)

class FrontendUserForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput)

    class Meta:
        model = CustomUser
        fields = '__all__'
        exclude = ['company']


class MusterForm(forms.ModelForm):
    class Meta:
        model = Muster
        fields = '__all__'
        


# class SalaryForm(forms.ModelForm):
#     class Meta:
#         model = Salary
#         fields = '__all__'



# class SalaryForm(forms.ModelForm):
#     employee_id = forms.CharField(max_length=50, required=True, label='Employee ID')  # Text input for employee ID
#     month = forms.DateField(
#         widget=forms.DateInput(attrs={'type': 'date'}),  # This makes the field a date input
#         required=True,
#         label='Month'
#     )

#     class Meta:
#         model = Salary
#         fields = ['employee_id', 'month', 'current_month_calculated_days', 'current_month_paid_days', 
#                   'basic_salary', 'house_rent_allowance', 'special_allowance', 'conveyance_allowance', 
#                   'pf_contribution', 'professional_tax', 'income_tax', 'performance_bonus', 
#                   'other_incentives', 'medical_insurance', 'stationery_misc', 'deductions', 
#                   'gross_salary', 'net_salary', 'total_variable_pay', 'per_day_salary', 'actual_salary', 
#                   'loan_deductions']
#         exclude = ['employee']  # We won't use the Employee field directly here.

#     def clean_employee_id(self):
#         employee_id = self.cleaned_data['employee_id']
#         try:
#             employee = Employee.objects.get(employee_id=employee_id)  # Check if the employee exists
#         except Employee.DoesNotExist:
#             raise forms.ValidationError("Employee with this ID does not exist.")
#         return 

from django import forms
from .models import Employee, Salary

class SalaryForm(forms.ModelForm):
    employee_id = forms.CharField(max_length=50, required=True, label='Employee ID')

    month = forms.DateField(
        widget=forms.DateInput(attrs={'type': 'date'}),
        required=True,
        label='Month'
    )

    class Meta:
        model = Salary
        exclude = ['employee']  # We're setting it manually based on employee_id

    def clean_employee_id(self):
        employee_id = self.cleaned_data['employee_id']
        try:
            employee = Employee.objects.get(employee_id=employee_id)
        except Employee.DoesNotExist:
            raise forms.ValidationError("Employee with this ID does not exist.")
        self.cleaned_data['employee'] = employee  # Add it for use later
        return employee_id

    def save(self, commit=True):
        salary = super().save(commit=False)
        salary.employee = self.cleaned_data['employee']  # Assign actual Employee instance
        if commit:
            salary.save()
        return salary


# class EmployeeProfileForm(forms.ModelForm):
#     class Meta:
#         model = Employee
#         fields = '__all__'


class EmployeeProfileForm(forms.ModelForm):
    class Meta:
        model = Employee
        exclude = ['user', 'company_name']  # ❗ exclude fields set in view or model

    date_of_birth = forms.DateField(
        widget=forms.DateInput(attrs={'type': 'date'}),
    )



class Company_checkForm(forms.ModelForm):
    class Meta:
        model = Company_check
        fields = '__all__'


class HolidaysForm(forms.ModelForm):
    class Meta:
        model = Holiday
        exclude = ['company']
    date=forms.DateField(
        widget=forms.DateInput(attrs={'type': 'date'}),
    )

# class LeaveForm(forms.ModelForm):
#     class Meta:
#         model = Leave
#         fields = '__all__'

from django import forms
from .models import Leave, CustomUser

class LeaveForm(forms.ModelForm):
    employee = forms.ModelChoiceField(
        queryset=CustomUser.objects.all(),
        label='Employee',
        required=True
    )

    class Meta:
        model = Leave
        fields = ['employee', 'advance_privilege_leave', 'sick_leave', 'casual_leave']

    def clean_employee_id(self):
        employee_id = self.cleaned_data.get('employee_id')
        try:
            employee = CustomUser.objects.get(employee_id=employee_id)  # Match employee by employee_id
        except CustomUser.DoesNotExist:
            raise forms.ValidationError("No employee found with the provided ID.")
        return employee

# class PersonalInfoForm(forms.ModelForm):
#     class Meta:
#         model = Employee
#         fields = [
#             'name', 
#             'date_of_birth', 
#             'gender', 
#             'nationality', 
#             'phone_number', 
#             'address',
#         ]


class PersonalInfoForm(forms.ModelForm):
    date_of_birth = forms.DateField(
        widget=forms.DateInput(attrs={'type': 'date'}),
        required=True
    )
   
    gender = forms.ChoiceField(
        choices=[('Male', 'Male'), ('Female', 'Female'), ('Other', 'Other')],
        widget=forms.Select(attrs={'class': 'form-control'})
    )
   
    phone_number = forms.CharField(
        validators=[RegexValidator(regex=r'^\+?\d{10,15}$')],
        widget=forms.TextInput(attrs={'readonly': 'readonly'})
    )
 
    class Meta:
        model = Employee
        fields = ['name', 'date_of_birth', 'gender', 'nationality', 'phone_number', 'address']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'nationality': forms.TextInput(attrs={'class': 'form-control'}),
            'address': forms.TextInput(attrs={'class': 'form-control'}),
        }
 


class ProfessionalInfoForm(forms.ModelForm):
    class Meta:
        model = Employee
        fields = [
            'designation', 
            'department', 
            'reporting_manager', 
            'employee_type', 
            'work_location', 
        ]


class BankingInfoForm(forms.ModelForm):
    class Meta:
        model = Employee
        fields = [
            'bank_account_number', 
            'bank_name', 
            'ifsc_code', 
            'aadhar_number', 
            'pan_number', 
            'uan_number',
        ]


class EmployeeMediaForm(forms.ModelForm):
    class Meta:
        model = EmployeeMedia
        fields = ['profile_picture', 'cover_picture']

from django import forms
from .models import HRContact
from app.models import Employee

class HRContactForm(forms.ModelForm):
    class Meta:
        model = HRContact
        fields = ['employee', 'role']
        widgets = {
            'employee': forms.Select(attrs={'class': 'form-control'}),
            'role': forms.Select(attrs={'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        company = kwargs.pop('company', None)
        super().__init__(*args, **kwargs)

        if company:
            exclude_ids = HRContact.objects.filter(
                employee__company=company
            ).exclude(pk=self.instance.pk).values_list('employee_id', flat=True)

            employee_queryset = Employee.objects.filter(company=company).exclude(id__in=exclude_ids)

            # Custom label formatting: EMP ID - Name
            self.fields['employee'] = forms.ModelChoiceField(
                queryset=employee_queryset,
                widget=forms.Select(attrs={'class': 'form-control'}),
                label='Employee',
                required=True
            )
            self.fields['employee'].label_from_instance = lambda obj: f"{obj.employee_id} - {obj.name}"

from django import forms
from django.contrib.auth import get_user_model
from .models import HelpDeskTicket, HRContact, Employee

User = get_user_model()

class HelpDeskTicketForm(forms.ModelForm):
    team_leader = forms.ModelChoiceField(
        queryset=User.objects.none(),
        label='Team Leader',
        required=True
    )
    hr = forms.ModelChoiceField(
        queryset=User.objects.none(),
        label='HR',
        required=True
    )
    manager = forms.ModelChoiceField(
        queryset=User.objects.none(),
        label='Manager',
        required=True
    )
    issue_type = forms.ChoiceField(choices=[], label='Issue Type', required=True)

    class Meta:
        model = HelpDeskTicket
        fields = ['issue_type', 'description', 'team_leader', 'hr', 'manager']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 3, 'placeholder': 'Describe your issue'}),
        }

    def __init__(self, *args, **kwargs):
        category = kwargs.pop('category', None)  # 'HR', 'IT', 'AS'
        company = kwargs.pop('company', None)    # <-- new
        super().__init__(*args, **kwargs)

        # Set issue type choices based on category
        if category == 'HR':
            choices = HelpDeskTicket.HR_ISSUE_CHOICES
        elif category == 'IT':
            choices = HelpDeskTicket.IT_ISSUE_CHOICES
        elif category == 'AS':
            choices = HelpDeskTicket.AS_ISSUE_CHOICES
        else:
            choices = []

        # Add empty placeholder choice at the beginning
        self.fields['issue_type'].choices = [('', '--- Select Issue Type ---')] + choices

        # Set TL and HR queryset using the new ForeignKey-based HRContact model
        if company:
            tl_contacts = HRContact.objects.filter(role='TL', employee__company=company)
            hr_contacts = HRContact.objects.filter(role='HR', employee__company=company)
            manager_contacts = HRContact.objects.filter(role='MG', employee__company=company)

            self.fields['team_leader'].queryset = User.objects.filter(id__in=tl_contacts.values_list('employee__user_id', flat=True))
            self.fields['hr'].queryset = User.objects.filter(id__in=hr_contacts.values_list('employee__user_id', flat=True))
            self.fields['manager'].queryset = User.objects.filter(id__in=manager_contacts.values_list('employee__user_id', flat=True))


class TaskForm(forms.Form):
    task_name = forms.CharField(max_length=255)
    employee_emails = forms.CharField(max_length=1024)  # For comma-separated emails
    due_date = forms.DateField(widget=forms.SelectDateWidget())  # Date widget for picking a due date
from django import forms
from .models import Team

class TeamForm(forms.ModelForm):
    class Meta:
        model = Team
        fields = ['name', 'members']
        widgets = {
            'members': forms.CheckboxSelectMultiple
        }
    
    def __init__(self, *args, user=None, **kwargs):
        super().__init__(*args, **kwargs)
        if user:
            # Only show users from the same company
            self.fields['members'].queryset = CustomUser.objects.filter(
                employee__company=user.employee.company
            )



class PersonalInfoForm(forms.ModelForm):
        class Meta:
            model = Employee
            fields = [
             'name',
             'date_of_birth',
             'gender',
             'nationality',
             'phone_number',
             'address',
         ]
            
#------------------------------------------------------------- Training #
from django import forms
from .models import TrainingTopic

class TrainingTopicForm(forms.ModelForm):
    class Meta:
        model = TrainingTopic
        fields = ['title', 'topic_link']