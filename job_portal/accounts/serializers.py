from rest_framework import serializers
from .models import CustomUser,JobPosting

class UserSignupSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)
    confirm_password = serializers.CharField(write_only=True)

    class Meta:
        model = CustomUser
        fields = ['username', 'email', 'password', 'confirm_password', 'role', 'qualification', 'skills', 'pan_no', 'company_name', 'address', 'resume', 'profile', 'first_name', 'last_name']

    def validate(self, data):
        if data['password'] != data['confirm_password']:
            raise serializers.ValidationError("Passwords do not match.")
        return data

    def create(self, validated_data):
        password = validated_data.pop('confirm_password')
        user = CustomUser(**validated_data)
        user.set_password(password) 
        user.save()
        return user
class JobPostingSerializer(serializers.ModelSerializer):
    class  Meta :
        model = JobPosting
        fields ='__all__'

    
    def create(self, validated_data):
        # This method is used to create a new JobPosting instance
        print("Creating job posting with data:", validated_data)
        return JobPosting.objects.create(**validated_data)