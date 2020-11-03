import json
from django.shortcuts import render, redirect, reverse
from django.http import HttpResponse, JsonResponse
from accounts import sso

def main(request):
    if request.session.get('status'):
        return redirect('project_main')
    else:
        return redirect('login')
