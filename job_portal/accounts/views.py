from rest_framework.response import Response
from rest_framework import status
from rest_framework.views import APIView
from .serializers import UserSignupSerializer,JobPostingSerializer
from django.contrib.auth import authenticate
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.permissions import IsAuthenticated
from .models import JobPosting
from django.core.files.storage import default_storage
from .models import CustomUser, JobPosting
from rest_framework.parsers import MultiPartParser, FormParser
from .serializers import JobPostingSerializer

class SignupView(APIView):
    def post(self, request):
        serializer = UserSignupSerializer(data=request.data)
        
        if serializer.is_valid():
            serializer.save()
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
        else:
            return Response({
                'detail': 'Invalid credentials.'
            }, status=status.HTTP_401_UNAUTHORIZED)
class UserDetailsView(APIView):
    permission_classes = [IsAuthenticated]  # Ensure that only authenticated users can access this

    def get(self, request):
        user = request.user  # The currently authenticated user
        # Respond with user details (username and role)
        return Response({
            'username': user.username,
            'role': user.role,  # Assuming the 'role' field is available in your CustomUser model
        })

#utsab
class JobPostingView(APIView):
    def get(self,request):
        try:
            jobs = JobPosting.objects.all()
            serializer = JobPostingSerializer(jobs, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def post(self, request):
        serializer = JobPostingSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
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

        # Update user fields if they are provided in the request
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
 #utsab   
class ResumeUploadView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        user = request.user
        if 'resume' not in request.FILES:
            return Response({"error": "No resume file provided"}, status=status.HTTP_400_BAD_REQUEST)

        resume_file = request.FILES['resume']
        
        # Save the file to the user's resume field
        user.resume = resume_file
        user.save()

        # Get the URL of the saved file
        file_url = user.resume.url

        return Response({"resume": file_url}, status=status.HTTP_201_CREATED)

#utsab
class RecommendedJobsView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user  # Get the authenticated user

        # Fetch all job postings
        jobs = JobPosting.objects.all()
        job_serializer = JobPostingSerializer(jobs, many=True)

        # Return user profile and job postings
        return Response({
            "user": {
                "skills": user.skills,
                "job_type": user.role,  # Assuming role is used for job type preference
                "experience_level": user.qualification,  # Assuming qualification is used for experience level
            },
            "jobs": job_serializer.data,
        }, status=status.HTTP_200_OK)