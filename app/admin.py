from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from app.models import *
from app.forms import *

# Register your models here.

admin.site.register(Company_check)
admin.site.register(Muster)
admin.site.register(Employee)
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

class CustomUserAdmin(UserAdmin):

    add_form = UserCreationForm
    list_display = ('employee_id', 'email', 'password', 'first_name', 'last_name', 'last_login', 'date_joined', 'role', 'is_superuser', 'is_staff', 'is_active')
    ordering = ('employee_id',)

    fieldsets = (
        (None, {'fields': ('password', 'first_name', 'last_name', 'last_login', 'date_joined', 'role', 'groups')}),
        )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('employee_id', 'email', 'first_name', 'last_name', 'password', 'last_login', 'date_joined', 'role', 'user_permissions', 'is_superuser', 'is_staff', 'is_active')}
            ),
        )

    filter_horizontal = ('groups', 'user_permissions')

admin.site.register(CustomUser, CustomUserAdmin)