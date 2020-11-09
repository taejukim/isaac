from django.contrib import admin
from apps.testcase.models import Service, Function, Testcase, Procedure\
    ,Region, Testcase_history, Procedure_history

admin.site.register(Service)
admin.site.register(Function)
admin.site.register(Testcase)
admin.site.register(Procedure)
admin.site.register(Region)
admin.site.register(Testcase_history)
admin.site.register(Procedure_history)
