from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from app.models import *
from app.forms import *

# Register your models here.

admin.site.register(Company_check)
admin.site.register(Muster)
admin.site.register(Team)
# app/admin.py


admin.site.register(HRContact)


admin.site.register(Salary)
admin.site.register(TimeEntry)
admin.site.register(Notification)
admin.site.register(Task)
admin.site.register(Leave)
admin.site.register(LeaveRequest)
admin.site.register(ExpenseClaim)
admin.site.register(LoanRequest)
admin.site.register(Holiday)
admin.site.register(Performance)
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser

class CustomUserAdmin(UserAdmin):
    add_form = UserCreationForm  # ✅ Your custom form

    list_display = (
        'employee_id', 'email', 'first_name', 'last_name',
        'role', 'company', 'is_superuser', 'is_staff', 'is_active'
    )
    ordering = ('employee_id',)

    fieldsets = (
        (None, {
            'fields': (
                'employee_id', 'email', 'password', 'first_name', 'last_name',
                'role', 'company', 'is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions'
            )
        }),
        ('Important dates', {'fields': ('last_login', 'date_joined')}),
    )

    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': (
                'employee_id', 'email', 'first_name', 'last_name',
                'role', 'company', 'password',  # ✅ Just 'password', not password1/password2
                'is_superuser', 'is_staff', 'is_active', 'groups', 'user_permissions'
            )
        }),
    )

    filter_horizontal = ('groups', 'user_permissions')


admin.site.register(CustomUser, CustomUserAdmin)

from django.contrib import admin
from .models import Employee, EmployeeMedia

class EmployeeMediaInline(admin.StackedInline):
    model = EmployeeMedia
    extra = 0

@admin.register(Employee)
class EmployeeAdmin(admin.ModelAdmin):
    inlines = [EmployeeMediaInline]


admin.site.register(EmployeeMedia)
