from rest_framework.response import Response
from rest_framework import status
from rest_framework.views import APIView
from .serializers import UserSignupSerializer,JobPostingSerializer
from django.contrib.auth import authenticate
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.permissions import IsAuthenticated


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

class JobPostingView(APIView):
    def post(self, request):
        print("Incoming request data:", request.data)  # Log the incoming data
        serializer = JobPostingSerializer(data=request.data)
        
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        
        print("Invalid data:", serializer.errors)  # Debug invalid data
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)