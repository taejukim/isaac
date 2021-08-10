from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
from accounts.login_session import login_required
from accounts.views import get_session
from django.views.decorators.csrf import csrf_exempt
from apps.testcase.models import Function, Service, Testcase

import json

# /testcase
# @login_required
def main(request):
    session = get_session(request)
    testcases = Service.objects.all()
    target_service = request.GET.get('service', "sms")
    service = testcases.get(service_id=target_service)
    target_module = service.module_set.first().module_id
    module = service.module_set.get(module_id=target_module)
    target_function = module.function_set.first().function_id
    function = module.function_set.all()
    testcase_list = []
    for f in function:
        testcase_list += f.testcase_set.all().values("testcase_id", "summary", "priority", "author")
    
    context = {
        'testcases': testcases,
        'service' : service,
        'module' : module,
        'testcase_list':json.dumps(testcase_list),
        'user_info':dict(session),
        'app_name':'testcase',
    }
    return render(request, 'testcase/main.html', context)

# /testcase/functions
@login_required
def functions(request):
    return get_ajax_data(request, Service, 'service_id', 'function_set')
   
# /testcase/testcases
@login_required
def testcases(request):
    return get_ajax_data(request, Function, 'function_id', 'testcase_set')

# /testcase/procedures
@login_required
def procedures(request):
    get_ajax_data(request, Testcase, 'testcase_id', 'procedure_set')

@login_required
def testcases(request):
    get_ajax_data(request, Testcase, 'testcase_id', 'procedure_set')


# @csrf_exempt
def get_ajax_data(request, model, key, set_key):
    if request.POST:
        id = request.POST.get('target_id', None)
        entity = model.objects.get(**{key:id})
        retv = getattr(entity, set_key).values()
        return JsonResponse(list(retv), safe=False)
    else:
        return HttpResponse(False)

@csrf_exempt
def get_testcase(request, testcase_id):
    templates = 'testcase/testcase.html'
    context = {'testcase':Testcase.objects.get(testcase_id=testcase_id)}
    return render(request, templates, context)