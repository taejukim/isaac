from django.contrib import admin
from django.contrib.auth.models import Group
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from accounts.models import User
from django.utils.translation import gettext, gettext_lazy as _ # for i18n

class UserAdmin(BaseUserAdmin):
    list_display = ('username', 'kr_name', 'title', 'department', 
                    'email', 'is_staff','is_superuser', 'is_member')
    list_filter = ('is_staff',)
    fieldsets = ( # 기본 Field set
        (None, {'fields': ('kr_name', 'email', 'emp_no','password')}),
        (_('Personal info'), {
            'fields': ('title', 'position', 'department', 'img_src', 'dept_code')
            }),
        (_('Permissions'), {
            'fields': ('is_staff', 'is_superuser', 'is_active', 
                                'is_member', 'user_permissions')
            }),
        (_('Important dates'), {'fields': ('last_login', 'date_joined')}),
    )

    add_fieldsets = ( # User 추가 Field set
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'password1', 'password2'),
        }),
        (_('Personal info'), {
            'fields': ('title', 'position', 'department', 'img_src', 'dept_code')
            }),
        (_('Permissions'), {'fields': ('is_staff', 'is_superuser', 'is_member')}),
        (_('Important dates'), {'fields': ('last_login', 'date_joined')}),
    )
    
    search_fields = ('kr_name', 'emp_no', )

admin.site.register(User, UserAdmin)
admin.site.unregister(Group)
