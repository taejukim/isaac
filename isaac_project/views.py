import json

from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
from isaac_project import sso

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
