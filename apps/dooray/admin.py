from django.contrib import admin
from apps.dooray.models import UserList, TargetProject, Tags

admin.site.register(UserList)
admin.site.register(TargetProject)

@admin.register(Tags)
class TagsAdmin(admin.ModelAdmin):
    search_fields = ('tag_name', 'tag_type', 'tag_class', )
    list_display=['project', 'tag_id', 'tag_name', 'tag_type','tag_class',]
