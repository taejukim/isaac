"""isaac URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.1/topics/http/urls/
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
from django.urls import path, include
from isaac_project import views
from apps import project, testcase, problem, testing
# import accounts
from accounts import views as accounts_views

urlpatterns = [
	path('admin/', admin.site.urls),
    path('', views.main, name='login'), # Landing
    path('login/', accounts_views.login, name='login'),
    path('logout/', accounts_views.logout, name='logout'),
    # path('login/', accounts.views.login, name='login'),
    # path('logout/', accounts.views.logout, name='logout'),
    path('testing/', include('apps.testing.urls'), name='testing_main'),
    path('project/', include('apps.project.urls'), name='project_main'),
    path('testcase/', include('apps.testcase.urls'), name='testcase_main'),
    path('problem/', include('apps.problem.urls'), name='problem_main'),
	]
