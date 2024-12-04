from django.contrib import admin
from .models import CustomUser, Qualification
# Register your models here.

class CustomUserAdmin(admin.ModelAdmin):
    list_display = ('username', 'email', 'isEmployer')
    list_filter = ['isEmployer']
    search_fields = ('username', 'email')

admin.site.register(CustomUser, CustomUserAdmin)


admin.site.register(Qualification)