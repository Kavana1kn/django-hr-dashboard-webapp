import re
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from .models import Employee

# Simulated persistence mock data layer for the internal grid dashboard
DEMO_DATA = [
    {"employee_id": "EMP001", "name": "Smitha rao", "role": "HR Manager", "department": "Human Resources", "email": "smith@cognizant.com"},
    {"employee_id": "EMP002", "name": "Jairaj tiwari", "role": "Software Engineer", "department": "Engineering", "email": "jairaj@cognizant.com"},
]

def signup_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard_home')
        
    if request.method == "POST":
        username = request.POST.get('username', '').strip()
        password = request.POST.get('password', '')
        confirm_password = request.POST.get('confirm_password', '')

        # 1. Username Regex Validation (letters, numbers, underscores allowed)
        if not re.match(r'^[a-zA-Z0-9_]+$', username):
            return render(request, 'dashboard/signup.html', {'error': 'Username can include letters, numbers, and underscores only.'})

        # 2. Duplicate Account Check
        if User.objects.filter(username=username).exists():
            return render(request, 'dashboard/signup.html', {'error': 'That username is already taken.'})

        # 3. Password Number Requirement Check
        if not any(char.isdigit() for char in password):
            return render(request, 'dashboard/signup.html', {'error': 'Password must contain at least one numerical digit (0-9).'})

        # 4. Confirmation Matching Check
        if password != confirm_password:
            return render(request, 'dashboard/signup.html', {'error': 'Passwords do not match.'})

        # Logic passes validation: Commit record creation
        user = User.objects.create_user(username=username, password=password)
        login(request, user)
        return redirect('dashboard_home')

    return render(request, 'dashboard/signup.html')


def login_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard_home')

    if request.method == "POST":
        username = request.POST.get('username', '').strip()
        password = request.POST.get('password', '')

        # Validate Username pattern input on Login side
        if not re.match(r'^[a-zA-Z0-9_]+$', username):
            return render(request, 'dashboard/login.html', {'error': 'Invalid username format.'})

        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('dashboard_home')
        else:
            return render(request, 'dashboard/login.html', {'error': 'Invalid username or password credentials.'})

    return render(request, 'dashboard/login.html')


def logout_view(request):
    logout(request)
    return redirect('login')


@login_required(login_url='login')
def dashboard_home(request):
    # Initialize DB with demo data if empty
    if Employee.objects.count() == 0:
        for item in DEMO_DATA:
            Employee.objects.create(
                employee_id=item['employee_id'],
                name=item['name'],
                role=item.get('role', ''),
                department=item.get('department', ''),
                email=item.get('email', ''),
            )

    search_query = request.GET.get('search', '').strip()

    employees_qs = Employee.objects.all()
    if search_query:
        employees_qs = employees_qs.filter(
            Q(name__icontains=search_query) |
            Q(department__icontains=search_query) |
            Q(role__icontains=search_query) |
            Q(employee_id__icontains=search_query)
        )

    edit_emp = None
    edit_id = request.GET.get('edit_id')
    if edit_id:
        edit_emp = Employee.objects.filter(employee_id=edit_id).first()

    total_count = Employee.objects.count()
    distinct_depts = Employee.objects.values_list('department', flat=True).distinct().count()

    if request.method == "POST":
        action = request.POST.get('action')
        emp_id = request.POST.get('employee_id', '').strip()

        if action == "delete":
            Employee.objects.filter(employee_id=emp_id).delete()
            return redirect('dashboard_home')

        elif action == "save":
            form_mode = request.POST.get('form_mode', 'CREATE')

            if form_mode == 'CREATE' and not emp_id:
                existing_ids = [int(e.employee_id.replace('EMP', '')) for e in Employee.objects.filter(employee_id__startswith='EMP')]
                next_id_num = max(existing_ids) + 1 if existing_ids else 1
                emp_id = f"EMP{next_id_num:03d}"

            if form_mode == 'CREATE' and Employee.objects.filter(employee_id=emp_id).exists():
                return render(request, 'dashboard/index.html', {
                    'employees': employees_qs, 'edit_emp': edit_emp, 'error_msg': f"ID {emp_id} is already assigned!",
                    'total_count': total_count, 'distinct_depts': distinct_depts, 'username': request.user.username
                })

            name = request.POST.get('name', 'Unnamed Employee').strip()
            role = request.POST.get('role', 'General Staff').strip()
            department = request.POST.get('department', '').strip()
            email = request.POST.get('email', 'info@company.com').strip()

            # Create or update the Employee record
            obj, created = Employee.objects.update_or_create(
                employee_id=emp_id,
                defaults={
                    'name': name,
                    'role': role,
                    'department': department,
                    'email': email,
                }
            )
            return redirect('dashboard_home')

    context = {
        'employees': employees_qs,
        'edit_emp': edit_emp,
        'search_query': request.GET.get('search', ''),
        'total_count': total_count,
        'distinct_depts': distinct_depts,
        'username': request.user.username
    }
    return render(request, 'dashboard/index.html', context)