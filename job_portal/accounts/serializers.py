# accounts/serializers.py
from rest_framework import serializers
from .models import CustomUser, JobPosting, JobApplication, JobApply,Message
from django.conf import settings
import os
from .content_based import read_pdf_manually, preprocess, compute_tf, compute_idf, compute_vector, cosine_similarity

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
        validated_data.pop('confirm_password')
        user = CustomUser(**validated_data)
        user.set_password(validated_data['password'])
        user.save()
        return user

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ['id', 'username', 'latitude', 'longitude']  # Include coordinates for distance calculation

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ['id', 'username', 'latitude', 'longitude']

class JobPostingSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)

    class Meta:
        model = JobPosting
        fields = '__all__'

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        experience_levels = {1: "Entry Level", 2: "Mid Level", 3: "Senior Level"}
        representation['experience_level'] = experience_levels.get(instance.experience_level, "Unknown")
        job_types = {'full_time': "Full Time", 'part_time': "Part Time"}
        representation['job_type'] = job_types.get(instance.job_type, instance.job_type)
        return representation

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
        fields = '__all__'
        read_only_fields = ('first_name', 'last_name')

# accounts/serializers.py
# accounts/serializers.py
class JobApplicationGetSerializer(serializers.ModelSerializer):
    score = serializers.SerializerMethodField()

    class Meta:
        model = JobApply
        fields = ['id', 'user', 'first_name', 'last_name', 'resume', 'phone_no', 'expected_salary', 'job_id', 'score', 'status']  # Added 'id'

    def get_score(self, obj):
        # Existing get_score method remains unchanged...
        job_posting = obj.job_id
        if not job_posting or not obj.resume:
            return 0.0

        job_text = ' '.join([
            job_posting.job_title or '',
            job_posting.job_description or '',
            str(job_posting.experience_level) if job_posting.experience_level else '',
            str(job_posting.min_salary) if job_posting.min_salary else '',
            str(job_posting.max_salary) if job_posting.max_salary else '',
            job_posting.company_address or '',
            job_posting.job_type or '',
            job_posting.requirements or ''
        ])
        
        resume_path = os.path.join(settings.MEDIA_ROOT, str(obj.resume))
        if not os.path.exists(resume_path):
            return 0.0

        resume_content = read_pdf_manually(resume_path)
        if not resume_content:
            return 0.0

        job_tokens = preprocess(job_text)
        resume_tokens = preprocess(resume_content)
        all_docs = [resume_tokens, job_tokens]
        idf = compute_idf(all_docs)
        resume_tf = compute_tf(resume_tokens)
        job_tf = compute_tf(job_tokens)
        keywords = list(idf.keys())
        resume_vector = compute_vector(resume_tokens, keywords, resume_tf, idf)
        job_vector = compute_vector(job_tokens, keywords, job_tf, idf)
        score = cosine_similarity(resume_vector, job_vector)
        
        phrase_bonus = sum(1 for phrase in preprocess(job_posting.requirements or '') 
                          if phrase in ' '.join(resume_tokens) and phrase in job_text) * 0.05
        
        final_score = min(score + phrase_bonus, 1.0)
        return round(final_score, 4)

class MessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Message
        fields = ['id', 'sender', 'recipient', 'job_application', 'content', 'timestamp', 'is_read']
        read_only_fields = ['sender', 'timestamp', 'is_read']