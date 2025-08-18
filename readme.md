# aihr4u
LORAHRMS
# HR4U - Human Resource Management System
A full-featured HRMS (Human Resource Management System) built using Django and Django REST Framework (DRF). This system manages key HR operations including employee onboarding, attendance tracking, payroll, task assignment, and internal notifications — providing an all-in-one platform for efficient human resource management.

## Features
- ✅ Role-based login system (Admin, HR, Manager, Employee)
- ✅ Employee CRUD operations
- ✅ Attendance (Muster) tracking
- ✅ Leave and loan requests
- ✅ Expense claims
- ✅ Task assignment
- ✅ Notification system
- ✅ Salary management
- ✅ File uploads with validation
- ✅ Excel/PDF export
- ✅ Real-time updates using WebSocket
- ✅ API integration with JWT authentication
- ✅ 404 & error pages
- ✅ Admin dashboard and employee dashboard

## Tech Stack
- **Backend**: Django, Django REST Framework
- **Database**: PostgreSQL      
- **Task Queue**: Celery with Redis             |
- **Real-time Features**: WebSocket / socket.io          
- **Performance & Security**: Rate Limiting and Caching

## Installation and Setup Instructions
1. **Create Project Directory**
   ```bash
   mkdir HR4U
   cd HR4U
2. **Set Up a Virtual Environment**
   ```bash
   python -m venv env
   env\Scripts\activate  # On Windows
3. **Install all project dependencies**
   ```bash
   pip install \
   django \
   djangorestframework \
   djangorestframework-simplejwt \
   psycopg2-binary \
   python-decouple \
   python-dotenv \
   dj-database-url \
   celery \
   redis \
   channels \
   whitenoise \
   geoip2 \
   openpyxl \
   requests
4. **Create Django Project and App**
   ```bash
   django-admin startproject project
   cd project
   python manage.py startapp app
5. **Make changes in settings.py**
   - Add 'app', to the INSTALLED_APPS list.
   - Add 'rest_framework', 'rest_framework_simplejwt', 'crispy_forms', and 'crispy_bootstrap4' as well.
   - Configure Database in settings.py ( Used default Database)
6. **Apply Migrations**
   ```bash
   python manage.py makemigrations
   python manage.py migrate
7. **Final Setup and Run**
   ```bash
   python manage.py createsuperuser  # Create Superuser for admin panel
   python manage.py runserver   # Run the Development Server
   pip freeze > requirements.txt  # Create Requirements File

8. **Folder Structure**
   ```bash
   HR4U/
   ├── project/                      # Main Django project (settings and configuration)
   │   ├── __init__.py
   │   ├── settings.py               # Global settings
   │   ├── urls.py                   # Root URL configuration
   │   ├── wsgi.py                   # WSGI entry-point for deployment
   │   └── asgi.py                   # ASGI entry-point for async support
   │
   ├── app/                          # Core Django app (business logic)
   ├── __init__.py
   │   ├── admin.py                  # Admin panel configuration
   │   ├── apps.py
   │   ├── models.py                 # Models: User, Property, Booking, etc.
   │   ├── serializers.py            # Data validation & transformation
   │   ├── urls.py                   # App-level routing
   │   ├── utils.py                  # Utility functions (OTP, helper logic)
   │   └── views.py                  # Business logic & API views
   │
   ├── templates/                    # HTML templates
   │   ├── base.html
   │   ├── login.html
   │   ├── dashboard.html
   │   └── ...                       # Other HTML pages
   │
   ├── static/                       # CSS, JS, images
   │   └── ...
   │
   ├── media/                        # Uploaded files (images, PDFs, etc.)
   │
   ├── migrations/                   # Django model migrations
   │
   ├── .env                          # Environment variables (not committed)
   ├── .gitignore                    # Files/folders to exclude from Git
   ├── manage.py                     # Django management utility
   ├── requirements.txt              # Python dependencies
   └── README.md                     # Project documentation

## Development Workflow
**Create templates**
This Django project includes the following templates located in the templates
**Core Pages:**
- 404.html – Custom 404 error page
- base.html – Base layout used by other templates
- index.html – Home or landing page
- login.html – User login page
- dashboard.html – User dashboard view
**Employee Management:**
- employee_create.html, employee_edit.html, employee_delete.html, employee_form.html, employee_list.html, employee_detail.html, view_employee.html
**Leave & Holiday Management:**
- leave_create.html, leave_edit.html, leave_list.html, leave_detail.html, leave_balance.html
- holiday_create.html, holiday_edit.html, holidays_list.html, holiday_view.html, holidays.html
**Performance & Salary:**
- performance_entry.html, performance_list.html, performance_page.html
- salary_details.html, salary_list.html, create_salary.html, edit_salary.html
- review_muster.html, muster_status.html, muster.html, working_days.html
**Forms & Policies:**
- company_form.html, company_create.html, company_edit.html, company_list.html, company_delete.html
- acceptable_use_policy.html, refund_cancellation_policy.html, cookie_policy.html, terms_of_service.html, policy.html, data_retention_policy.html
**User & Auth:**
- reset_password.html, reset_password_with_otp.html, forgot_password.html, verify_otp.html, user_form.html, user_list.html, user_confirm_delete.html
**User & Auth:**
- faq.html, contact_us.html, chat_bot.html, profile.html, loan_requests.html, tax_deduction.html, task_list.html, task_management.html, staff_notifications.html, training.html, all_payslips.html, view_salary.html, expense_claims.html  
## Implementation
1. Define Models
Describe data structures for each feature (Employee, Leave, Salary, etc.).
2. Create Forms
Build Django forms (ModelForm) to handle user input for models.
3. Implement Views
Write function-based or class-based views to process data and render templates.
4. Set Up URLs
Map views to URLs in both app-level and project-level urls.py.
5. Connect Everything
Integrate models, views, forms, URLs, and templates to make features functional.