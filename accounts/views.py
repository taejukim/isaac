import json
from django.shortcuts import render, redirect, reverse
from django.http import HttpResponse, JsonResponse, HttpResponseRedirect
from django.contrib.auth import authenticate
from django.contrib.auth import login as auth_login
from accounts.models import User
from accounts import sso

def login(request):
    if request.method == 'POST': # Post 요청(로그인 요청)
        post_data = request.POST
        emp_no = post_data.get('emp_no')
        pw = post_data.get('pw')
        user_info = sso.check_sso(emp_no, pw)
        if not user_info: # login fail
            return redirect('login')
        user_entity = check_django_user(request, emp_no, pw, user_info)
        if user_entity:
            if user_entity.is_member:
                return redirect(request.session.get('next') or 'project_main')
            else: # Not Isaac memeber
                return render(request, 'no_member.html', {})
        else:
            return redirect('login')
    else: # Get 요청
        if request.session.get('status'):
            return redirect(request.session.get('next') or 'project_main')
        return render(request, 'login.html', {'next':request.session.get('next')})

def logout(request):
    # Logout 시 Session 정보 삭제 후 로그인 페이지로 이동
    try:
        request.session.clear()
    except:
        for key in request.session.keys():
            del request.session[key]
    return redirect('login')

def set_session(request, emp_no, user_info):
    # 세션 설정
    request.session['status'] = 'True'
    request.session['emp_no'] = emp_no
    request.session['kr_name'] = user_info['kr_name']
    request.session['title'] = user_info['title']
    request.session['position'] = user_info['position']
    request.session['department'] = user_info['department']
    request.session['dept_code'] = user_info['dept_code']
    request.session['img_src'] = user_info['img_src']
    request.session['email'] = user_info['email']
    request.session.set_expiry(60*60*24*7) # 7 days
    return True

def get_session(request):
    session = request.session
    return {
        'status':session.get('status'),
        'emp_no':session.get('emp_no'),
        'kr_name':session.get('kr_name'),
        'title':session.get('title'),
        'position':session.get('position'),
        'department':session.get('department'),
        'dept_code':session.get('dept_code'),
        'img_src':session.get('img_src'),
        'email':session.get('email')      
    }

def check_django_user(request, emp_no, pw, user_info):
    # Django User 모델에서 SSO 성공으로 전달된 emp_no 를 검색하여 존재 여부 확인
    try:
        user_entity = User.objects.all().get(username = emp_no)
    except:
        user_entity = None

    if user_entity:
        if not authenticate(username = emp_no, password = pw):
            # Password가 바뀐 경우 Password 수정을 위해 emp_no 와 신규 pw 를 modify_password에 전달
            modify_password(emp_no, pw)
        # 정상 로그인 진행 시 해당 계정의 세션을 설정하기 위해 set_session에 emp_no, user_info를 전달
        auth_login(request, authenticate(username = emp_no, password = pw))
        set_session(request, emp_no, user_info)
        return user_entity
    else:
        # Django User에 해당 emp_no 가 없는 경우 ID 추가를 위해 insert_user함수에 계정 정보를 전달
        return insert_user(request, emp_no, pw, user_info)
    
def insert_user(request, emp_no, pw, user_info):
    # 새로운 User 생성
    new_user = User.objects.create_user(username = emp_no, password = pw)
    new_user.kr_name = user_info['kr_name']
    new_user.emp_no = user_info['emp_no']
    new_user.title = user_info['title']
    new_user.position = user_info['position']
    new_user.department = user_info['department']
    new_user.dept_code = user_info['dept_code']
    new_user.img_src = user_info['img_src']
    new_user.email = user_info['email']
    # new_user.is_member = True
    new_user.save()
    auth = authenticate(username = emp_no, password = pw)
    auth_login(request, auth)
    set_session(request, emp_no, user_info) 
    return new_user
    
def modify_password(emp_no, password):
    # Password 변경
    user = User.objects.get(username=emp_no)
    user.set_password(password)
    user.save()
    return True
