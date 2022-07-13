from django.contrib import admin
from apps.resources.models import ServiceInfo, Member, WorkHistory, Category

@admin.register(ServiceInfo)
class ServiceInfoAdmin(admin.ModelAdmin):
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
