from django.contrib import admin
from apps.resources.models import ServiceInfo, Resource

@admin.register(ServiceInfo)
class ServiceInfoAdmin(admin.ModelAdmin):
    search_fields = ('category', 'name_detail', )
    list_display=['id', 'service_no', 'sort', 'category',
        'name_detail','priority', 'group', 'team_member', 'create_dt', ]

@admin.register(Resource)
class ResourceAdmin(admin.ModelAdmin):
    search_fields = ('category', 'service_no', 'name_detail',)
    list_display = ['id', 'service_no', 'mm', 'month', 'year', 'category', 'name_detail', 'create_dt']
