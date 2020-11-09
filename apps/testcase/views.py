from django.http import request
from django.shortcuts import render
from django.http import HttpResponse
from django.db.models import Q, Max, Min, Case, When, F, Count
from accounts.login_session import login_required
from accounts.views import get_session

from apps.testcase.models import Service

# /testcase
@login_required
def main(request):
    session = get_session(request)
    testcases = Service.objects.all()
    context = {
        'testcases': testcases,
        'user_info':dict(session)
    }
    return render(request, 'testcase/main.html', context)

# /testcase/functions
@login_required
def functions(request):
    if request.is_ajax():
        service_id = request.POST.get('service_id', None)
        functions = Service.objects.get(service_id=service_id)
        

        return HttpResponse(json.dumps(functions), content_type="application/json")


# /testcase/testcases
@login_required
def testcases(request):
    pass

# /testcase/procedures
@login_required
def procedures(request):
    pass

def search_user(request):
    if request.is_ajax():
        query = request.POST.get("name", "")
        users = LDAPUsers.objects.filter(Q(kr_name__icontains=query))[:50]
        result = []
        for user in users:
            _user = {
                'adid':user.adid,
                'kr_name':user.kr_name,
                'title':user.title,
                'dept':user.department,
                'email':user.email
                }
            result.append(_user)
        return HttpResponse(json.dumps(result), content_type="application/json")
