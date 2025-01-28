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
    
class JobPosting(models.Model):
    JOB_TYPE_CHOICES = [
        ('full_time', 'Full Time'),
        ('part_time', 'Part Time'),
    ]

    EXPERIENCE_LEVEL_CHOICES = [
        (1, 'Entry Level'),
        (2, 'Mid Level'),
        (3, 'Senior Level'),
    ]

    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    company_name = models.CharField(max_length=200, editable=False)
    company_address = models.CharField(max_length=200, null=True, blank=True)
    job_title = models.CharField(max_length=200)
    job_type = models.CharField(max_length=50, choices=JOB_TYPE_CHOICES, null=True)
    experience_level = models.IntegerField(choices=EXPERIENCE_LEVEL_CHOICES, null=True)
    job_description = models.TextField(max_length=500, null=True, blank=True)
    requirements = models.TextField(max_length=500, null=True, blank=True)

    def __str__(self):
        return f"{self.job_title} at {self.company_name}"

    def save(self, *args, **kwargs):
         self.company_name = self.user.company_name
         super().save(*args, **kwargs)