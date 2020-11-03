import json
from django.shortcuts import render, redirect, reverse
from django.http import HttpResponse, JsonResponse, HttpResponseRedirect
from accounts import sso

def login(request):
    if request.method == 'POST': # Post 요청(로그인 요청)
        post_data = request.POST
        emp_no = post_data.get('emp_no')
        pw = post_data.get('pw')
        result = sso.check_sso(emp_no, pw)
        if not result: # login fail
            return HttpResponse('login fail!')
        set_session(request, emp_no, result)
        return redirect(request.session.get('next') or 'project_main')
    else: # Get 요청
        if request.session.get('status'):
            return redirect(request.session.get('next') or 'project_main')
        return render(request, 'login.html', {})

def logout(request):
    try:
        request.session.clear()
    except:
        for key in request.session.keys():
            del request.session[key]
    request.session['next'] = request.session.get('next') or 'project_main'
    return HttpResponseRedirect(reverse('login'))

def set_session(request, emp_no, context):
    # 세션 설정
    request.session['status'] = 'True'
    request.session['emp_no'] = emp_no
    request.session['user_name'] = context['kr_name']
    request.session['title'] = context['title']
    request.session['position'] = context['position']
    request.session['department'] = context['department']
    request.session['dept_code'] = context['dept_code']
    request.session['img_src'] = context['img_src']
    request.session['email'] = context['email']
    request.session.set_expiry(60*60*24*7) # 7 days
    return request.session.get('_set_expiry')

def get_session(request):
    sessions = request.session
    return {
        'status':sessions.get('status'),
        'emp_no':sessions.get('emp_no'),
        'user_name':sessions.get('user_name'),
        'title':sessions.get('title'),
        'position':sessions.get('position'),
        'department':sessions.get('department'),
        'dept_code':sessions.get('dept_code'),
        'img_src':sessions.get('img_src'),
        'email':sessions.get('email')      
    }
