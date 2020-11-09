from django.shortcuts import render
from django.http import HttpResponse
from accounts.login_session import login_required
from accounts.views import get_session
from django.views.decorators.csrf import csrf_exempt
from apps.testcase.models import Function, Service, Testcase

# /testcase
# @login_required
def main(request):
    session = get_session(request)
    testcases = Service.objects.all()
    context = {
        'testcases': testcases,
        'user_info':dict(session)
    }
    return render(request, 'testcase/main.html', context)

# /testcase/functions
# @login_required
@csrf_exempt
def functions(request):
    return get_ajax_data(request, Service, 'service_id')
   
# /testcase/testcases
# @login_required
def testcases(request):
    return get_ajax_data(request, Function, 'function_id')

# /testcase/procedures
# @login_required
def procedures(request):
    get_ajax_data(request, Testcase, 'testcase_id')

@csrf_exempt
def get_ajax_data(request, model, key):
    if request.POST:
        id = request.POST.get(key, None)
        entity = model.objects.filter(**{key:id})
        return HttpResponse(list(entity.values()), content_type='application/json')
    else:
        return HttpResponse(False)
