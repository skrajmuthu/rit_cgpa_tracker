from django.shortcuts import render, redirect, get_object_or_404
from .form import Student_form,userform
from django.db.models import Q

from .models import Student,User
from datetime import datetime
from django.contrib.auth import login as auth_login
from django.contrib.auth import authenticate
from django.contrib.auth import logout as auth_logout
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
import os
from django.core.paginator import Paginator
from django.conf import settings
import pandas as pd
from datetime import datetime
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import render
import json
from django.urls import reverse
from django.http import FileResponse
from django.contrib import messages





def encrypt_password(raw_password):
    # Implement your password encryption algorithm (e.g., using hashlib)
    import hashlib
    return hashlib.sha256(raw_password.encode()).hexdigest()


def signup(request):
    if request.method == 'POST':
        form = userform(request.POST)   
        if form.is_valid():
            password = form.cleaned_data['Password']
            confirm_password = form.cleaned_data['conform_Password']
            if password == confirm_password:
                encrypted_password = encrypt_password(password)

                # Save the encrypted password to your user model
                user = form.save(commit=False)  # Don't save the form yet
                user.Password = encrypted_password
                user.conform_Password = encrypted_password

                user.save()

                # Redirect to a success page or login page
                return redirect('login')
            else:
                # Passwords don't match, return an error
                form.add_error('confirm_password', 'Passwords do not match')
                return render(request, "auth/signup.html", {'form': form})
        else:
            return render(request, "error.html", {'form': form})
    else:
        form = userform()

    return render(request, "auth/signup.html", {'form': form})


def login(request):
    if request.method == 'POST':
        
        email = request.POST.get('email')
        password = request.POST.get('password')

        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            # User not found, show an error message
            error_message = 'Invalid staff_id or password.'
            return render(request, "auth/login.html", {'error_message': error_message})

        # Check if the password matches
        if user.Password == encrypt_password(password):
            request.session['user_auth'] = True
            request.session['login_role'] = 'teacher'
            request.session['user']={"username":user.user_name,'email':email,'deportment':user.Department}
            role = 'teacher'
            base_url = reverse('dashboard')  # Get the base URL for the 'dashboard' view
            query_string = f'?role={role}'  # Construct the query string
            url = base_url + query_string  # Combine the base URL and query string
            return redirect(url)
        else:
            # Passwords don't match, show an error message
            error_message = 'Invalid username or password.'
            return render(request, "auth/login.html", {'error_message': error_message})
    else:
        return render(request, "auth/login.html")


def index(request):
    return render(request, 'index.html')



def student(request):
    role = request.GET.get('role')
    current_year = datetime.now().year
    batch_years = [f'{year}-{(year + 4) % 100:02d}' for year in range(current_year - 4, current_year + 1)]
    try:
        teacher_role = request.session.get('user')['deportment']
    except TypeError:
        teacher_role = None
    if request.method == 'POST':
        reg_no = request.POST.get('reg_no')
        data = Student.objects.filter(reg_no=reg_no)
        if data:
            
            reg_value = get_object_or_404(Student, reg_no=reg_no)
            if role == 'teacher' and request.session.get('user_auth') :
                return render(request, 'update.html',{"reg_value":reg_value,"batch_years":batch_years,'role':role,'teacher_role':teacher_role})
            elif role == 'student':
                return render(request, 'student_view.html',{"reg_value":reg_value,"batch_years":batch_years,'role':role,'teacher_role':teacher_role})
            else:
                return redirect('login')
        if role == 'teacher' and request.session.get('user_auth'):
            return render(request, 'add.html',{"reg_no":reg_no,"batch_years":batch_years,'role':role,'teacher_role':teacher_role})
        else:
            return render(request, 'student.html',{'role':role,'teacher_role':teacher_role})
    if  role == 'student':
        return render(request, 'student.html',{'role':role,'teacher_role':teacher_role})
    elif role == 'teacher' and request.session.get('user_auth'):
        return render(request, 'student.html',{'role':role,'teacher_role':teacher_role})
    else:
        return redirect('login')


def insert_grade(request):
    current_year = datetime.now().year
    batch_years = [f'{year}-{(year + 4) % 100:02d}' for year in range(current_year - 4, current_year + 1)]
    if request.method == 'POST':
        reg_no = request.POST.get('reg_no')
        try:
            student = Student.objects.get(reg_no=reg_no)
            form = Student_form(request.POST, instance=student)  # Load existing student data into the form
        except Student.DoesNotExist:
            form = Student_form(request.POST)

        if form.is_valid():
            sem1 = float(form.cleaned_data.get('semester1')) if form.cleaned_data.get('semester1') is not None else None
            sem2 = float(form.cleaned_data.get('semester2')) if form.cleaned_data.get('semester2') is not None else None
            sem3 = float(form.cleaned_data.get('semester3')) if form.cleaned_data.get('semester3') is not None else None
            sem4 = float(form.cleaned_data.get('semester4')) if form.cleaned_data.get('semester4') is not None else None
            sem5 = float(form.cleaned_data.get('semester5')) if form.cleaned_data.get('semester5') is not None else None
            sem6 = float(form.cleaned_data.get('semester6')) if form.cleaned_data.get('semester6') is not None else None
            sem7 = float(form.cleaned_data.get('semester7')) if form.cleaned_data.get('semester7') is not None else None
            sem8 = float(form.cleaned_data.get('semester8')) if form.cleaned_data.get('semester8') is not None else None

            # Calculate CGPA based on available semesters
            # if sem8 is not None and sem8!=0:
            #     cgpa = (sem1 + sem2 + sem3 + sem4 + sem5 + sem6 + sem7 + sem8) / 8
            # elif sem7 is not None and sem7!=0:
            #     cgpa = (sem1 + sem2 + sem3 + sem4 + sem5 + sem6 + sem7) / 7
            # elif sem6 is not None and sem6!=0:
            #     cgpa = (sem1 + sem2 + sem3 + sem4 + sem5 + sem6) / 6
            # elif sem5 is not None and sem5!=0:
            #     cgpa = (sem1 + sem2 + sem3 + sem4 + sem5) / 5
            # elif sem4 is not None and sem4!=0:
            #     cgpa = (sem1 + sem2 + sem3 + sem4) / 4
            # elif sem3 is not None and sem3!=0:
            #     cgpa = (sem1 + sem2 + sem3) / 3
            # elif sem2 is not None and sem2!=0:
            #     cgpa = (sem1 + sem2) / 2
            # elif sem1 is not None and sem1!=0:
            #     cgpa = sem1

            # cgpa=round(cgpa,4)

            # Save the form data to the student object
            user = form.save(commit=False)
            # user.cgpa = cgpa
            user.sem1 = sem1
            user.sem2 = sem2
            user.sem3 = sem3
            user.sem4 = sem4
            user.sem5 = sem5
            user.sem6 = sem6
            user.sem7 = sem7
            user.sem8 = sem8
            user.save()
            # messages.success(request, 'Data successfully added/updated.')
            return render(request,'student.html',{'message':"Data successfully added/updated."})

        else:
            print('Form errors:', form.errors)  # Debug print for form errors
            return render(request, 'error.html', {'form': form})

    return render(request, 'add.html',{"batch_years":batch_years})

from datetime import datetime

def dashboard(request):
    role = request.GET.get('role')
    if role == 'teacher' and request.session.get('user_auth'):
        user=request.session.get('user', {})
        user_name=user['username']
        current_year = datetime.now().year
        batch_years = [f'{year}-{(year + 4) % 100:02d}' for year in range(current_year - 4, current_year + 1)]
        user = request.session.get('email')
        teacher_role = request.session.get('user')['deportment']
        try:
            data = Student.objects.all() if teacher_role == 'All' else Student.objects.filter(department=teacher_role)
        except Student.DoesNotExist:
            data = None 
        students = Student.objects.all()
        if request.method == 'POST':
            cgpa = request.POST.get('cgpa')
            department = request.POST.get('department')
            history_of_arrear = request.POST.get('history_of_arrear')
            bag_of_log = request.POST.get('bag_of_log')
            batch = request.POST.get('batch')
            sslc = request.POST.get('sslc')
            hsc = request.POST.get('hsc')
            semesters = request.POST.getlist('semester')
            gpa = request.POST.get('gpa')
            
            if cgpa:
                students = students.filter(cgpa__gte=cgpa)
            if teacher_role == 'All':
                if department and department != 'All':
                    students = students.filter(department=department)
            else:
                students = students.filter(department=teacher_role)
            
            if history_of_arrear:
                students = students.filter(history_of_arrear__lte=history_of_arrear)
            
            if bag_of_log:
                if bag_of_log == 'Yes & No':
                    # No filter needed as we want both Yes and No
                    pass
                else:
                    students = students.filter(bag_of_log=bag_of_log)
            
            if batch:
                students = students.filter(batch=batch)
            
            if sslc:
                students = students.filter(sslc__gte=sslc)
            
            if hsc:
                students = students.filter(hsc__gte=hsc)
            
            if semesters and gpa:
                semester_filters = Q()  # Initialize an empty Q object for AND operation
                for sem in semesters:
                    # Create a filter for each semester
                    semester_filter = Q(**{f'{sem}__gte': gpa})
                    # Combine all semester filters with AND operation
                    semester_filters &= semester_filter
                
                students = students.filter(semester_filters)

            return render(request, 'hod/dashboard.html',{"batch_years":batch_years,"data":students,'role':role,'teacher_role':teacher_role})
        return render(request, 'hod/dashboard.html',{"batch_years":batch_years,"data":data,'role':role,'teacher_role':teacher_role})
    else:
        return redirect('login')
    

def download_excel(request):
    # Define the path to the file
    file_path = os.path.join(settings.BASE_DIR,'static\\requred_files', 'sample_student_data.xlsx')
    # Serve the file as an attachment
    response = FileResponse(open(file_path, 'rb'), as_attachment=True, filename='cgpa_formate.xlsx')
    return response


def upload_cgpa(request):
    teacher_role = request.session.get('user')['deportment']
    data = Student.objects.filter(department=teacher_role)
    if request.method == 'POST':
        excel_file = request.FILES['file']

        # Get the expected columns from the form
        form = Student_form()
        expected_columns = list(form.fields.keys())

        # Read the Excel file using pandas
        try:
            df = pd.read_excel(excel_file)
        except Exception as e:
            messages.error(request, f'Error reading Excel file: {str(e)}')
            return redirect('upload_cgpa')

        # Verify the columns in the uploaded file
        if not all(column in df.columns for column in expected_columns):
            messages.error(request, 'The uploaded file does not match the required format.')
            return redirect('upload_cgpa')
        other_department=[]
        # Loop through each row in the DataFrame and update or create Student records
        for index, row in df.iterrows():
            reg_no = row['reg_no']
            if row['department'] == teacher_role:
                defaults = {
                    'batch': row['batch'],
                    'student_name': row['student_name'],
                    'department': row['department'],
                    'cgpa': row['cgpa'],
                    'sslc': row['sslc'],
                    'hsc': row['hsc'],
                    'bag_of_log': row['bag_of_log'],
                    'history_of_arrear': row['history_of_arrear'],
                    'semester1': row['semester1'],
                    'semester2': row['semester2'],
                    'semester3': row['semester3'],
                    'semester4': row['semester4'],
                    'semester5': row['semester5'],
                    'semester6': row['semester6'],
                    'semester7': row['semester7'],
                    'semester8': row['semester8']
                }

                student, created = Student.objects.update_or_create(
                    reg_no=reg_no, defaults=defaults
                )
            else:
                other_department.append(reg_no)
                continue
        print('-------------------',other_department)
        if len(other_department) >=1 :
            message=f'Currect Student data uploaded successfully! But this reg numbers have issue in department column {other_department} '
            messages.success(request,message )
        else:
            message ='Student data uploaded successfully!'
            messages.success(request, message)
        return render(request, 'hod/dashboard.html',{"data":data,'message':message,'teacher_role':teacher_role})

    return render(request, 'hod/dashboard.html',{"data":data,'teacher_role':teacher_role})

def logout (request):
    request.session.flush()
    return redirect('index')