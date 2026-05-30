import re
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required

# Simulated persistence mock data layer for the internal grid dashboard
DEMO_DATA = [
    {"employee_id": "EMP001", "name": "Alice Smith", "role": "HR Manager", "department": "Human Resources", "email": "alice@company.com"},
    {"employee_id": "EMP002", "name": "Bob Jones", "role": "Software Engineer", "department": "Engineering", "email": "bob@company.com"},
]

def signup_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard_home')
        
    if request.method == "POST":
        username = request.POST.get('username', '').strip()
        password = request.POST.get('password', '')
        confirm_password = request.POST.get('confirm_password', '')

        # 1. Username Regex Validation (Alphanumeric only, no special characters)
        if not re.match(r'^[a-zA-Z0-9]+$', username):
            return render(request, 'dashboard/signup.html', {'error': 'Username cannot contain spaces or special characters.'})

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
        if not re.match(r'^[a-zA-Z0-9]+$', username):
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
    # Ensure session data array exists securely
    if 'employees' not in request.session:
        request.session['employees'] = DEMO_DATA

    employees = request.session['employees']
    search_query = request.GET.get('search', '').strip().lower()

    if search_query:
        employees = [
            emp for emp in employees 
            if search_query in emp['name'].lower() or 
               search_query in emp['department'].lower() or 
               search_query in emp['role'].lower() or
               search_query in emp['employee_id'].lower()
        ]

    edit_emp = None
    edit_id = request.GET.get('edit_id')
    if edit_id:
        edit_emp = next((emp for emp in request.session['employees'] if emp['employee_id'] == edit_id), None)

    total_count = len(request.session['employees'])
    distinct_depts = len(set(emp['department'] for emp in request.session['employees']))

    if request.method == "POST":
        action = request.POST.get('action')
        emp_id = request.POST.get('employee_id', '').strip()
        current_list = request.session['employees']

        if action == "delete":
            current_list = [emp for emp in current_list if emp['employee_id'] != emp_id]
            request.session['employees'] = current_list
            return redirect('dashboard_home')

        elif action == "save":
            form_mode = request.POST.get('form_mode', 'CREATE')
            
            if form_mode == 'CREATE' and not emp_id:
                existing_ids = [int(emp['employee_id'].replace('EMP', '')) for emp in current_list if emp['employee_id'].startswith('EMP')]
                next_id_num = max(existing_ids) + 1 if existing_ids else 1
                emp_id = f"EMP{next_id_num:03d}"
            elif form_mode == 'CREATE' and any(emp['employee_id'] == emp_id for emp in current_list):
                return render(request, 'dashboard/index.html', {
                    'employees': employees, 'edit_emp': edit_emp, 'error_msg': f"ID {emp_id} is already assigned!",
                    'total_count': total_count, 'distinct_depts': distinct_depts, 'username': request.user.username
                })

            payload = {
                "employee_id": emp_id,
                "name": request.POST.get('name', 'Unnamed Employee').strip(),
                "role": request.POST.get('role', 'General Staff').strip(),
                "department": request.POST.get('department'),
                "email": request.POST.get('email', 'info@company.com').strip(),
            }

            current_list = [emp for emp in current_list if emp['employee_id'] != emp_id]
            current_list.append(payload)
            current_list.sort(key=lambda x: x['employee_id'])
            request.session['employees'] = current_list
            return redirect('dashboard_home')

    context = {
        'employees': employees,
        'edit_emp': edit_emp,
        'search_query': request.GET.get('search', ''),
        'total_count': total_count,
        'distinct_depts': distinct_depts,
        'username': request.user.username  # Read securely from authenticated request target
    }
    return render(request, 'dashboard/index.html', context)