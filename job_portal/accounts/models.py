# accounts/models.py
from django.db import models
from django.contrib.auth.models import AbstractUser
from rest_framework import serializers
from django.contrib.auth import get_user_model

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
    latitude = models.FloatField(null=True, blank=True)
    longitude = models.FloatField(null=True, blank=True)
    resume = models.FileField(upload_to='resumes/', null=True, blank=True)
    role = models.CharField(max_length=20, choices=JOB_ROLE_CHOICES, default='job_seeker')
    address = models.CharField(max_length=200, null=True)
    company_name = models.CharField(max_length=200, null=True)
    skills = models.CharField(max_length=100, null=True)
    qualification = models.CharField(max_length=50, choices=QUALIFICATION_CHOICES, null=True)
    pan_no = models.CharField(max_length=200, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']

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

    user = models.ForeignKey(get_user_model(), on_delete=models.CASCADE)
    company_name = models.CharField(max_length=200, editable=False)
    company_address = models.CharField(max_length=200, null=True, blank=True)
    job_title = models.CharField(max_length=200)
    job_type = models.CharField(max_length=50, choices=JOB_TYPE_CHOICES, null=True)
    experience_level = models.IntegerField(choices=EXPERIENCE_LEVEL_CHOICES, null=True)
    job_description = models.TextField(max_length=500, null=True, blank=True)
    requirements = models.TextField(max_length=500, null=True, blank=True)
    min_salary = models.IntegerField(null=True, blank=True)
    max_salary = models.IntegerField(null=True, blank=True)

    def __str__(self):
        return f"{self.job_title} at {self.company_name}"

    def save(self, *args, **kwargs):
        if not self.company_name and self.user and hasattr(self.user, 'company_name'):
            self.company_name = self.user.company_name or "Unnamed Company"
        super().save(*args, **kwargs)

class JobApply(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    first_name = models.CharField(max_length=200, null=True, blank=True)
    last_name = models.CharField(max_length=200, null=True, blank=True)
    resume = models.FileField(upload_to='jobapplied_resumes/', null=True, blank=True)
    phone_no = models.IntegerField(null=True, blank=True)
    expected_salary = models.IntegerField(null=True, blank=True)
    job_id = models.ForeignKey(JobPosting, on_delete=models.CASCADE, null=True)
    status = models.CharField(
        max_length=20,
        choices=[('applied', 'Applied'), ('contacted', 'Contacted'), ('selected', 'Selected')],
        default='applied'
    )

    def __str__(self):
        return f"Application by {self.first_name} {self.last_name}"

    def save(self, *args, **kwargs):
        if not self.first_name:
            self.first_name = self.user.first_name
        if not self.last_name:
            self.last_name = self.user.last_name
        super().save(*args, **kwargs)

class JobApplication(models.Model):
    job_id = models.IntegerField()
    user_id = models.IntegerField()
    
    def __str__(self):
        return f"Application for Job {self.job_id} by User {self.user_id}"
    
class Message(models.Model):
    sender = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name="sent_messages")
    recipient = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name="received_messages")
    job_application = models.ForeignKey(JobApply, on_delete=models.CASCADE, null=True)
    content = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)

    def __str__(self):
        return f"Message from {self.sender} to {self.recipient} about {self.job_application}"