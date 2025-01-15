from django.db import models
from django.contrib.auth.models import AbstractUser


class CustomUser(AbstractUser):

    QUALIFICATION_CHOICES = [
        ('SEE', 'SEE'),
        ('+2', '+2'),
        ('Under_graduate', 'Under Graduate'),
        ('Graduate', 'Graduate'),
        ('Masters', 'Masters'),
        ('PhD', 'PhD'),
    ]

    JOB_ROLE_CHOICES = [
        ('job_seeker', 'Job Seeker'),
        ('job_employer', 'Job Employer'),
    ]

    email = models.EmailField(unique=True)
    profile = models.ImageField(upload_to='profile/', null=True, blank=True)
    resume = models.FileField(upload_to='resumes/', null=True, blank=True)
    role = models.CharField(max_length=20, choices=JOB_ROLE_CHOICES, default='job_seeker')
    address = models.CharField(max_length=50, null=True)
    company_name = models.CharField(max_length=200, null=True)
    skills = models.CharField(max_length=100, null=True)
    qualification = models.CharField(max_length=50, choices=QUALIFICATION_CHOICES, null=True)
    pan_no = models.CharField(max_length=200, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    USERNAME_FIELD = 'email'  # Set email as the primary identifier
    REQUIRED_FIELDS = ['username']  # Fields required on createsuperuser


    def __str__(self):
          return self.username
