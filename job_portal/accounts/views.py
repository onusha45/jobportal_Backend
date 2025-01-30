from accounts.service import euclidean_distance
from rest_framework.response import Response
from rest_framework import status
from rest_framework.views import APIView
from .serializers import UserSignupSerializer, JobPostingSerializer
from django.contrib.auth import authenticate
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.permissions import IsAuthenticated
from .models import JobApply, JobPosting
from django.core.files.storage import default_storage
from .models import CustomUser, JobPosting
from rest_framework.parsers import MultiPartParser, FormParser
from .serializers import JobPostingSerializer
from .models import JobApplication  # Import your model
from .serializers import JobApplicationSerializer, JobApplySerializer  # Import the serializer
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.core.files.storage import default_storage


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

# utsab


class JobPostingView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        try:
            job_postings = JobPosting.objects.all().order_by('-id')  # Get all jobs, newest first
            serializer = JobPostingSerializer(job_postings, many=True)
            return Response(serializer.data)
        except Exception as e:
            print("Error fetching jobs:", str(e))
            return Response(
                {"detail": "Error fetching job postings"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    def post(self, request):
        try:
            data = request.data.copy()
            data['user'] = request.user.id

            serializer = JobPostingSerializer(data=data)
            if serializer.is_valid():
                instance = serializer.save()
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        except Exception as e:
            print("Error creating job posting:", str(e))
            return Response(
                {"detail": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


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

 # views.py


class EmployerProfileView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        # Ensure you're dealing with an employer user
        if user.role != 'job_employer':
            return Response({"detail": "Not authorized to access this profile."}, status=status.HTTP_403_FORBIDDEN)

        return Response({
            'username': user.username,
            'email': user.email,
            'company_name': user.company_name,  # Employer-specific field
            'address': user.address,

        })

 # utsab


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

# utsab


class RecommendedJobsView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user  # Get the authenticated user

        toggle = request.query_params.get('toggle', False)
        # Fetch all job postings
        jobs = JobPosting.objects.all()
        print(jobs)
        data = []
        for job in jobs:
        
            
            point1 = [user.longitude, user.latitude]
            point2 = [job.user.longitude, job.user.latitude]
            distance = euclidean_distance(point1, point2)
            

            # Add distance to the job data
            job_data = JobPostingSerializer(job).data  # Serialize the job data
            job_data['distance'] = distance  # Add the calculated distance
            data.append(job_data)
        print(type(toggle))   
        if toggle and toggle=="true":
            data.sort(key=lambda x: x['distance'])
        # Return user profile and job postings
        return Response({
            "user": {
                "skills": user.skills,
                "job_type": user.role,  # Assuming role is used for job type preference
                "experience_level": user.qualification,  # Assuming qualification is used for experience level
            },
            "jobs": data,
        }, status=status.HTTP_200_OK)


class ApplyJobView(APIView):
    def post(self, request):
        # Get data from request
        job_id = request.data.get('job_id')
        user_id = request.data.get('user_id')
        location = request.data.get('location')
        phone = request.data.get('phone')
        salary = request.data.get('salary')

        # Handle file upload
        resume = request.FILES.get('resume')  # Handling the file upload

        # Add debugging for received data
        print(
            f"Received data: job_id={job_id}, user_id={user_id}, location={location}, phone={phone}, salary={salary}, resume={resume}")

        # Check if the required fields are present
        if not all([job_id, user_id, location, phone, salary, resume]):
            return Response({"error": "All fields are required."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            # Create and save the JobApplication object
            job_application = JobApplication(
                job_id=job_id,
                user_id=user_id,
                location=location,
                phone=phone,
                salary=salary,
                resume=resume  # Save the file
            )
            job_application.save()

            print(f"Job Application saved with ID: {job_application.id}")

            # Serialize the saved job application (optional)
            serializer = JobApplicationSerializer(job_application)

            # Return success response with serialized data
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        except Exception as e:
            print(f"Error: {e}")
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class JobApplicationView(APIView):
    permission_classes = [IsAuthenticated]
    parser_classes = (MultiPartParser, FormParser)

    def post(self, request):
        try:
            user = request.user

            application_data = {
                'user': user.id,
                'location': request.data.get('location'),
                'resume': request.FILES.get('resume'),
                'phone_no': request.data.get('phone_no'),
                'expected_salary': request.data.get('expected_salary'),
                'job_id': request.data.get('job')
            }

            serializer = JobApplySerializer(data=application_data)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=status.HTTP_201_CREATED)  # Fixed
            else:
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)  # Fixed

        except Exception as e:
            print("Exception occurred:", str(e))
            return Response(
                {"error": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class JobApplicantDetailView(APIView):
    permission_classes = [IsAuthenticated]
    parser_classes = (MultiPartParser, FormParser)

    def get(self, request):
        try:
            user = request.user
            jobs = JobPosting.objects.filter(user=user.id).values_list("id")
            print(jobs)
            application_data = JobApply.objects.filter(job_id__in=jobs)
            print(application_data)
            serializer = JobApplySerializer(application_data, many=True)
            return Response(serializer.data)

        except Exception as e:
            print("Exception occurred:", str(e))
            return Response(
                {"error": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
