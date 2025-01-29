from django.contrib import admin
from .models import CustomUser,JobPosting,JobApply


class UserAdmin(admin.ModelAdmin):
    list_display = ['username', 'role']
    list_editable = ['role']

admin.site.register(CustomUser, UserAdmin)

admin.site.register(JobPosting)
admin.site.register(JobApply)
