from django.shortcuts import render, redirect

# Initial mock data for the dashboard demo
DEMO_DATA = [
    {"employee_id": "EMP001", "name": "Alice Smith", "role": "HR Manager", "department": "Human Resources", "email": "alice@company.com"},
    {"employee_id": "EMP002", "name": "Bob Jones", "role": "Software Engineer", "department": "Engineering", "email": "bob@company.com"},
]

def login_view(request):
    if request.method == "POST":
        request.session['is_logged_in'] = True
        request.session['username'] = request.POST.get('username', 'Admin User')
        return redirect('dashboard_home')
    return render(request, 'dashboard/login.html')

def logout_view(request):
    request.session.flush() 
    return redirect('login')

# CRITICAL: This is the exact function Django is complaining it can't find!
def dashboard_home(request):
    if not request.session.get('is_logged_in', False):
        return redirect('login')

    if 'employees' not in request.session:
        request.session['employees'] = DEMO_DATA

    employees = request.session['employees']
    search_query = request.GET.get('search', '').lower()

    if search_query:
        employees = [
            emp for emp in employees 
            if search_query in emp['name'].lower() or search_query in emp['department'].lower()
        ]

    edit_emp = None
    edit_id = request.GET.get('edit_id')
    if edit_id:
        edit_emp = next((emp for emp in request.session['employees'] if emp['employee_id'] == edit_id), None)

    total_count = len(request.session['employees'])
    distinct_depts = len(set(emp['department'] for emp in request.session['employees']))

    if request.method == "POST":
        action = request.POST.get('action')
        emp_id = request.POST.get('employee_id')
        current_list = request.session['employees']

        if action == "delete":
            current_list = [emp for emp in current_list if emp['employee_id'] != emp_id]
            request.session['employees'] = current_list
            return redirect('dashboard_home')

        elif action == "save":
            payload = {
                "employee_id": emp_id,
                "name": request.POST.get('name'),
                "role": request.POST.get('role'),
                "department": request.POST.get('department'),
                "email": request.POST.get('email'),
            }
            current_list = [emp for emp in current_list if emp['employee_id'] != emp_id]
            current_list.append(payload)
            request.session['employees'] = current_list
            return redirect('dashboard_home')

    context = {
        'employees': employees,
        'edit_emp': edit_emp,
        'search_query': request.GET.get('search', ''),
        'total_count': total_count,
        'distinct_depts': distinct_depts,
        'username': request.session.get('username')
    }
    return render(request, 'dashboard/index.html', context)