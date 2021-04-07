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
        module = Module.objects.get(module_id = module_id)
        functions = module.function_set.values('function_name', 'function_id')
        return JsonResponse({"data":list(functions)})
    return False