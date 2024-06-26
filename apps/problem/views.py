from django.shortcuts import render
from django.http import HttpResponse
from accounts.login_session import login_required
from accounts.views import get_session

@login_required
def main(request):
    session = get_session(request)
    context = {
        'app_name':'problem',
        'user_info':dict(session)
    }
    return render(request, 'problem/main.html', context)
