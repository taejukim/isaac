from django.shortcuts import redirect
from django.urls import reverse
from functools import wraps

# 각 페이지별 로그인 처리를 위한 데코레이터
def login_required(view):
    @wraps(view)
    def decorated(request, *args, **kwargs):
        session_info = request.session.get('status', False)
        if not session_info: # Log out or with out log in
            try:
                request.session.clear()
            except:
                for key in request.session.keys():
                    del request.session[key]
            return redirect(reverse('login'))
        request.session.set_expiry(60*60*24*7) # 세션 유효기간을 7일로 설정
        return view(request, *args, **kwargs)
    return decorated