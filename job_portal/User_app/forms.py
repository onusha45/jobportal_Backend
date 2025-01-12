from django import forms
from User_app.models import CustomUser

class Login(forms.Form):
    email = forms.CharField(max_length=150)
    password = forms.CharField(widget=forms.PasswordInput)

class UserSignup(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput)
    repassword = forms.CharField(widget=forms.PasswordInput)       
    profile = forms.ImageField(required=False)                                                     
    class Meta :
        model = CustomUser                                                                  
        fields = ['profile', 'username','email','password', 'repassword', 'isEmployer']

class EmployeerSignup(forms.ModelForm):
    class Meta :
        model = CustomUser
        fields = ['phone_no', 'address', 'company_name', 'pan_no']

class JobseekerSignup(forms.ModelForm):
    class Meta :
        model = CustomUser
        fields = ['first_name', 'last_name', 'qualification', 'resume', 'phone_no', 'address']