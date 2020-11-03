from django.shortcuts import redirect
from django.urls import reverse
from functools import wraps
from django.http import HttpResponseRedirect

# 각 페이지별 로그인 처리를 위한 데코레이터
def login_required(view):
    @wraps(view)
    def decorated(request, *args, **kwargs):
        login_status = request.session.get('status', False)
        income_path = request.path
        if not login_status: # Log out or with out log in
            try:
                request.session.clear()
            except:
                for key in request.session.keys():
                    del request.session[key]
            request.session['next'] = income_path
            return HttpResponseRedirect(reverse('login'))
        request.session.set_expiry(60*60*24*7) # 세션 유효기간을 7일로 설정
        if request.session.get('next'):
            del request.session['next']
        return view(request, *args, **kwargs)
    return decorated