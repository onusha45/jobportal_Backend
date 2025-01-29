from rest_framework import serializers
from accounts.models import CustomUser, JobPosting, JobApply
class JobApplySerializer(serializers.ModelSerializer):
    class Meta:
        model = JobApply
        fields = ['location', 'phone_no', 'expected_salary', 'resume']
        