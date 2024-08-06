"""
URL configuration for cpga_track project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from application import views
from application import duplicate


urlpatterns = [
    path('admin/', admin.site.urls),
    path('student', views.student, name="student"),
    path('', views.index, name="index"),
    path('insert_grade', views.insert_grade, name="insert_grade"),
    path('dashboard', views.dashboard, name="dashboard"),
    path('accadamic_details', views.accadamic_details, name="accadamic_details"),
    path('populate_fake_data', duplicate.populate_fake_data, name="populate_fake_data"),
    path('login', views.login, name="login"),
    path('signup', views.signup, name="signup"),
    path('download/', views.download_excel, name='download_excel'),
    path('upload/', views.upload_cgpa, name='upload_cgpa'),
    path('logout/', views.logout, name='logout'),
    path('visulaization/', views.visulaization, name='visulaization'),
    

]
