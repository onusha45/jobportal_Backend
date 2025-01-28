from django.contrib import admin
from .models import CustomUser,JobPosting,JobApply

admin.site.register(CustomUser)

admin.site.register(JobPosting)
admin.site.register(JobApply)
