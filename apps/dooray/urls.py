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
from apps.dooray import views, tasks

urlpatterns = [
    path('', tasks._main, name='dooray_main'),
    path('update', tasks._tag_update, name='dooray_tag_update'),
    path('issue', tasks._issue, name='dooray_issue'),
    path('grm', views.grm, name='get_grm' )
	]
