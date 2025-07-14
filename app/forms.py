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
    employee_id = forms.CharField(max_length=50, required=True, label='Employee ID')  # Text input for employee ID
    month = forms.DateField(
        widget=forms.DateInput(attrs={'type': 'date'}),  # This makes the field a date input
        required=True,
        label='Month'
    )

    class Meta:
        model = Salary
        fields = ['employee_id', 'month', 'current_month_calculated_days', 'current_month_paid_days', 
                  'basic_salary', 'house_rent_allowance', 'special_allowance', 'conveyance_allowance', 'total_fixed_salary',
                  'pf_contribution', 'professional_tax', 'income_tax', 'performance_bonus', 
                  'other_incentives', 'medical_insurance', 'stationery_misc', 'deductions', 
                  'gross_salary', 'net_salary', 'total_variable_pay', 'per_day_salary', 'actual_salary', 
                  'loan_deductions']
        exclude = []  # We include the 'employee' field here, so it can be saved in the model

    def clean_employee_id(self):
        employee_id = self.cleaned_data['employee_id']
        try:
            employee = Employee.objects.get(employee_id=employee_id)  # Check if the employee exists
        except Employee.DoesNotExist:
            raise forms.ValidationError("Employee with this ID does not exist.")
        return employee

    # Override the save method to assign the employee
    def save(self, commit=True):
        # Get the employee from cleaned data
        employee = self.cleaned_data.get('employee_id')
        
        # Create the Salary instance
        salary_instance = super().save(commit=False)
        
        # Assign the employee instance to the salary
        salary_instance.employee = employee

        if commit:
            salary_instance.save()
        return salary_instance


# class EmployeeProfileForm(forms.ModelForm):
#     class Meta:
#         model = Employee
#         fields = '__all__'


class EmployeeProfileForm(forms.ModelForm):
    class Meta:
        model = Employee
        fields = '__all__'

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
        fields = '__all__'
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
    employee_id = forms.CharField(max_length=100, label='Employee ID', required=True)

    class Meta:
        model = Leave
        fields = ['employee_id', 'advance_privilege_leave', 'sick_leave', 'casual_leave']
    
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


class ProfilePictureForm(forms.ModelForm):
    class Meta:
        model = Employee
        fields = ['profile_picture']


class CoverPictureForm(forms.ModelForm):
    class Meta:
        model = Employee
        fields = ['cover_picture']


class TaskForm(forms.Form):
    task_name = forms.CharField(max_length=255)
    employee_emails = forms.CharField(max_length=1024)  # For comma-separated emails
    due_date = forms.DateField(widget=forms.SelectDateWidget())  # Date widget for picking a due date