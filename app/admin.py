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
admin.site.register(HelpDeskTicket)

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


#------------------------------------------------------------- Training #
from .models import TrainingTopic

@admin.register(TrainingTopic)
class TrainingTopicAdmin(admin.ModelAdmin):
    list_display = ('title', 'created_by', 'company', 'created_at')
    search_fields = ('title', 'description', 'created_by__username')
    list_filter = ('company', 'created_at')
    readonly_fields = ('created_by', 'company', 'created_at')
    ordering = ('-created_at',)

    def save_model(self, request, obj, form, change):
        if not obj.pk:  # Only set created_by and company on creation
            obj.created_by = request.user
            obj.company = request.user.company
        super().save_model(request, obj, form, change)
