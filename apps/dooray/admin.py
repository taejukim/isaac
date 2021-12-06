from django.contrib import admin
from apps.dooray.models import Issues, QAMember, UserList, TargetProject, Tags

admin.site.register(UserList)
admin.site.register(TargetProject)
admin.site.register(Issues)
admin.site.register(QAMember)

@admin.register(Tags)
class TagsAdmin(admin.ModelAdmin):
    search_fields = ('tag_name', 'tag_type', 'tag_class', )
    list_display=['project', 'tag_id', 'tag_name', 'tag_type','tag_class',]

