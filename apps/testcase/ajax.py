from django.http.response import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from apps.testcase.models import Function, Service, Module

@csrf_exempt
def get_modules(request):
    if request.method == 'POST':
        post_data = request.POST
        service_id = post_data.get('service_id')
        service = Service.objects.get(service_id = service_id)
        modules = service.module_set.values('module_name', 'module_id')
        return JsonResponse({"data":list(modules)})
    return False

@csrf_exempt
def get_functions(request):
    if request.method == 'POST':
        post_data = request.POST
        module_id = post_data.get('module_id')
        service_id = post_data.get('service_id')
        modules = Module.objects.filter(service__service_id=service_id)
        module = modules.get(module_id=module_id)
        functions = module.function_set.values('function_name', 'function_id')
        return JsonResponse({"data":list(functions)})
    return False

@csrf_exempt
def get_testcases(request):
    if request.method == 'POST':
        post_data = request.POST
        service_id = post_data.get('service_id')
        module_id= post_data.get('module_id')
        function_id = post_data.get('function_id')
        if function_id == 'all':
            function = Function.objects.filter(module__module_id=module_id)\
                                        .filter(module__service__service_id=service_id)
            testcases = []
            for f in function:
                testcases += f.testcase_set.values(
                    'testcase_id',
                    'summary',
                    'priority',
                    'author',
                    )
        else:
            function = Function.objects.get(
                module__service__service_id=service_id,
                module__module_id=module_id,
                function_id=function_id
                )
            testcases = function.testcase_set.values(
                'testcase_id',
                'summary',
                'priority',
                'author',
                )
        return JsonResponse({"data":list(testcases)})
    return False