from django.db import models
from django.contrib.auth.models import AbstractUser
# Create your models here.


class Qualification(models.Model):
    qualification = models.CharField(max_length=150, null=True)

    def __str__(self):
        return self.qualification


class CustomUser(AbstractUser):
    email = models.EmailField(unique=True)
    profile = models.ImageField(upload_to='profile/', null=True, blank=True)
    resume = models.FileField(upload_to='resumes/', null=True, blank=True)
    isEmployer = models.BooleanField(default=False)
    phone_no =models.IntegerField(null=True)
    address = models.CharField(max_length=50, null=True)
    company_name = models.CharField(max_length=200, null=True)
    skills = models.CharField(max_length=100, null=True)
    qualification = models.ForeignKey(Qualification, on_delete=models.CASCADE, blank=True, null=True)
    pan_no = models.CharField(max_length=200, null=True)


    def __str__(self):
          return self.username


# class ContactUs(models.Model):
#     email = models.EmailField(unique=True)
#     profile = models.ImageField(upload_to='profile/', null=True, blank=True)
#     resume = models.FileField(upload_to='resumes/', null=True, blank=True)
#     isEmployer = models.BooleanField(default=False)
#     phone_no =models.IntegerField(null=True)
#     address = models.CharField(max_length=50, null=True)
#     company_name = models.CharField(max_length=200, null=True)
#     skills = models.CharField(max_length=100, null=True)
#     qualification = models.ForeignKey(Qualification, on_delete=models.CASCADE, blank=True, null=True)
#     pan_no = models.CharField(max_length=200, null=True)


#     def __str__(self):
#           return self.username





