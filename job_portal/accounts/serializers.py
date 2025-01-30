from rest_framework import serializers
from .models import CustomUser, JobPosting, JobApplication, JobApply


class UserSignupSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)
    confirm_password = serializers.CharField(write_only=True)

    class Meta:
        model = CustomUser
        fields = ['username', 'email', 'password', 'confirm_password', 'longitude', 'latitude', 'role', 'qualification',
                  'skills', 'pan_no', 'company_name', 'address', 'resume', 'profile', 'first_name', 'last_name']

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
    class Meta:
        model = JobPosting
        fields = '__all__'

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        # Convert experience level number to string
        experience_levels = {
            1: "Entry Level",
            2: "Mid Level",
            3: "Senior Level"
        }
        representation['experience_level'] = experience_levels.get(instance.experience_level, "Unknown")
        
        # Convert job_type from database format to display format
        job_types = {
            'full_time': "Full Time",
            'part_time': "Part Time"
        }
        representation['job_type'] = job_types.get(instance.job_type, instance.job_type)
        
        return representation
# In serializers.py


class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ['username', 'email', 'resume']


class JobApplicationSerializer(serializers.ModelSerializer):
    class Meta:
        model = JobApplication
        fields = ['job_id', 'user_id']


class JobApplySerializer(serializers.ModelSerializer):
    class Meta:
        model = JobApply
        fields = '_all_'
        read_only_fields = ('first_name', 'last_name')
