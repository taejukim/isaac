import json

from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
from accounts import sso

def login(request):
    if request.method == 'POST': # Post 요청(로그인 요청)
        post_data = request.POST
        emp_no = post_data.get('emp_no')
        pw = post_data.get('pw')
        result = sso.check_sso(emp_no, pw)
        # To do : login 정보를 담을 구조 정의
        if not result:
            return HttpResponse('login fail!')
        return JsonResponse(result)
    else: # Get 요청
        # To do : Login 폼 만들기
        return render(request, 'login.html', {})


def logout(request):
    return HttpResponse('Logout!')


def setSession(request, emp_no, context):
    # 세션 설정
    request.session['emp_no'] = emp_no
    request.session['user_name'] = context['user_name']
    request.session['title'] = context['title']
    request.session['position'] = context['position']
    request.session['department'] = context['department']
    request.session['dept_code'] = context['dept_code']
    request.session['img_src'] = context['img_src']
    request.session['email'] = context['email']
    request.session['status'] = context['status']
    request.session.set_expiry(60*60*24*7) # 7 days
    return request.session.get('_set_expiry')