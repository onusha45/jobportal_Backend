# accounts/views.py
from accounts.service import euclidean_distance

from rest_framework.response import Response
from rest_framework import status
from rest_framework.views import APIView
from .serializers import JobApplicationGetSerializer, UserSignupSerializer, JobPostingSerializer, MessageSerializer, JobApplySerializer
from django.contrib.auth import authenticate
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.permissions import IsAuthenticated
from .models import JobApply, JobPosting, CustomUser, JobApplication, Message
from rest_framework.parsers import MultiPartParser, FormParser
from django.conf import settings
import os

class SignupView(APIView):
    def post(self, request):
        serializer = UserSignupSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class LoginView(APIView):
    def post(self, request):
        email = request.data.get('email')
        password = request.data.get('password')
        user = authenticate(username=email, password=password)
        if user is not None:
            refresh = RefreshToken.for_user(user)
            access_token = str(refresh.access_token)
            return Response({
                'access': access_token,
                'refresh': str(refresh),
            }, status=status.HTTP_200_OK)
        return Response({
            'detail': 'Invalid credentials.'
        }, status=status.HTTP_401_UNAUTHORIZED)

class UserDetailsView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        return Response({
            'username': user.username,
            'role': user.role,
        })

# accounts/views.py (partial update for JobPostingView)
class JobPostingView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        try:
            job_postings = JobPosting.objects.all().order_by('-id')
            serializer = JobPostingSerializer(job_postings, many=True)
            return Response(serializer.data)
        except Exception as e:
            print("Error fetching jobs:", str(e))
            return Response({"detail": "Error fetching job postings"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def post(self, request):
        try:
            data = request.data.copy()
            # Do not add 'user' to data here since the serializer won't use it due to read_only=True
            serializer = JobPostingSerializer(data=data)
            if serializer.is_valid():
                # Explicitly set the user on the instance before saving
                instance = serializer.save(user=request.user)
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            print("Error creating job posting:", str(e))
            return Response({"detail": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class ProfileView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        return Response({
            'username': user.username,
            'email': user.email,
            'address': user.address,
            'first_name': user.first_name,
            'last_name': user.last_name,
            'qualification': user.qualification,
            'skills': user.skills,
            'resume': user.resume.url if user.resume else None,
        })

    def put(self, request):
        user = request.user
        data = request.data
        if 'first_name' in data:
            user.first_name = data['first_name']
        if 'last_name' in data:
            user.last_name = data['last_name']
        if 'qualification' in data:
            user.qualification = data['qualification']
        if 'username' in data:
            user.username = data['username']
        if 'email' in data:
            user.email = data['email']
        if 'address' in data:
            user.address = data['address']
        if 'skills' in data:
            user.skills = data['skills']
        user.save()
        return Response({
            'username': user.username,
            'email': user.email,
            'address': user.address,
            'first_name': user.first_name,
            'last_name': user.last_name,
            'qualification': user.qualification,
            'skills': user.skills,
            'resume': user.resume.url if user.resume else None,
        }, status=status.HTTP_200_OK)

class EmployerProfileView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        if user.role != 'job_employer':
            return Response({"detail": "Not authorized to access this profile."}, status=status.HTTP_403_FORBIDDEN)
        return Response({
            'username': user.username,
            'email': user.email,
            'company_name': user.company_name,
            'address': user.address,
        })

class ResumeUploadView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        user = request.user
        if 'resume' not in request.FILES:
            return Response({"error": "No resume file provided"}, status=status.HTTP_400_BAD_REQUEST)
        resume_file = request.FILES['resume']
        user.resume = resume_file
        user.save()
        file_url = user.resume.url
        return Response({"resume": file_url}, status=status.HTTP_201_CREATED)

class RecommendedJobsView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        toggle = request.query_params.get('toggle', 'false').lower() == 'true'

        try:
            jobs = JobPosting.objects.all()
            serializer = JobPostingSerializer(jobs, many=True)
            response_data = []

            for job in serializer.data:
                job_data = dict(job)
                job_user = job.get('user', {})

                if (user.latitude and user.longitude and 
                    job_user.get('latitude') and job_user.get('longitude')):
                    point1 = [float(user.longitude), float(user.latitude)]
                    point2 = [float(job_user['longitude']), float(job_user['latitude'])]
                    try:
                        distance = euclidean_distance(point1, point2)
                        print(f"Job {job['id']} distance: {distance} km")
                    except ValueError as e:
                        print(f"Distance calculation error: {e}")
                        distance = 999999
                else:
                    distance = 999999
                    print(f"Job {job['id']} missing coordinates, distance set to: {distance}")

                job_data['distance'] = distance
                response_data.append(job_data)

            if toggle:
                response_data.sort(key=lambda x: x['distance'])

            return Response({
                "user": {
                    "skills": user.skills,
                    "job_type": user.role,
                    "experience_level": user.qualification,
                },
                "jobs": response_data,
            }, status=status.HTTP_200_OK)

        except Exception as e:
            print(f"Error in recommendation: {e}")
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class ApplyJobView(APIView):
    def post(self, request):
        job_id = request.data.get('job_id')
        user_id = request.data.get('user_id')
        location = request.data.get('location')
        phone = request.data.get('phone')
        salary = request.data.get('salary')
        resume = request.FILES.get('resume')

        if not all([job_id, user_id, location, phone, salary, resume]):
            return Response({"error": "All fields are required."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            job_application = JobApplication(
                job_id=job_id,
                user_id=user_id,
                location=location,
                phone=phone,
                salary=salary,
                resume=resume
            )
            job_application.save()
            serializer = JobApplicationSerializer(job_application)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        except Exception as e:
            print(f"Error: {e}")
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

# accounts/views.py
class JobApplicationView(APIView):
    permission_classes = [IsAuthenticated]
    parser_classes = (MultiPartParser, FormParser)

    def post(self, request):
        try:
            user = request.user
            application_data = {
                'user': user.id,
                'phone_no': request.data.get('phone_no'),
                'expected_salary': request.data.get('expected_salary'),
                'job_id': request.data.get('job'),  # Match frontend's 'job'
                'resume': request.FILES.get('resume'),
                # Optionally store 'address' in another field or ignore it
            }
            serializer = JobApplySerializer(data=application_data)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            print("Exception occurred:", str(e))
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class JobApplicantDetailView(APIView):
    permission_classes = [IsAuthenticated]
    parser_classes = (MultiPartParser, FormParser)

    def get(self, request, job_id):
        try:
            jobs = JobPosting.objects.filter(id=job_id).values_list("id", flat=True)
            application_data = JobApply.objects.filter(job_id__in=jobs)
            serializer = JobApplicationGetSerializer(application_data, many=True)
            application_data = sorted(serializer.data, key=lambda x: x.get('score', 0), reverse=True)
            return Response(application_data)
        except Exception as e:
            print("Exception occurred:", str(e))
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class ListJobViewApi(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        try:
            user = request.user
            jobs = JobPosting.objects.filter(user=user.id)
            serializer = JobPostingSerializer(jobs, many=True)
            return Response(serializer.data)
        except Exception as e:
            print("Exception occurred:", str(e))
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        

class MessageView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        try:
            messages = Message.objects.filter(recipient=request.user).order_by('-timestamp')
            serializer = MessageSerializer(messages, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Exception as e:
            print(f"Error fetching messages: {e}")
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    def post(self, request):
        try:
            data = request.data.copy()
            serializer = MessageSerializer(data=data)
            if serializer.is_valid():
                # Fetch the JobApply instance to ensure it exists
                job_application_id = serializer.validated_data['job_application'].id
                try:
                    job_application = JobApply.objects.get(id=job_application_id)
                except JobApply.DoesNotExist:
                    return Response({"error": f"Job application with ID {job_application_id} does not exist"}, status=status.HTTP_400_BAD_REQUEST)

                # Save the message with sender and validated job_application
                message = serializer.save(sender=request.user)
                
                # Update JobApply status to 'contacted'
                job_application.status = 'contacted'
                job_application.save()
                
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            print(f"Error sending message: {str(e)} - Full data: {request.data}")
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class SeekerApplicationsView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        try:
            applications = JobApply.objects.filter(user=request.user)
            serializer = JobApplySerializer(applications, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Exception as e:
            print(f"Error fetching applications: {e}")
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)