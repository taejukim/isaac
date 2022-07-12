from django.contrib import admin
from apps.resources.models import ServiceInfo, Resource, \
    Service, Member, WorkHistory, Category


# @admin.register(ServiceInfo)
# class ServiceInfoAdmin(admin.ModelAdmin):
#     search_fields = ('category', 'name_detail', )
#     list_display=['id', 'service_no', 'sort', 'category',
#         'name_detail','priority', 'group', 'team_member', 'create_dt', ]

# @admin.register(Resource)
# class ResourceAdmin(admin.ModelAdmin):
#     search_fields = ('category', 'service_no', 'name_detail',)
#     list_display = ['id', 'service_no', 'mm', 'month', 'year', 'category', 'name_detail', 'create_dt']

@admin.register(Service)
class ServiceAdmin(admin.ModelAdmin):
    list_display = ['service', 'category', 'priority','man_month','ordering']

@admin.register(Member)
class MemberAdmin(admin.ModelAdmin):
    list_display = ['name', 'team', 'title', 'position']

@admin.register(WorkHistory)
class WorkHistoryAdmin(admin.ModelAdmin):
    list_display = ['service','work_type','test_type', 'man_days']

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['category', ]
