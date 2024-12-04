from rest_framework import viewsets,status
from .models import CustomUser
from .serializers import UsersSerializers,LoginSerializer
from rest_framework.permissions import IsAuthenticated
from django.contrib.auth import authenticate
from rest_framework.response import Response
from rest_framework.authtoken.models import Token



class UsersViewsets(viewsets.ModelViewSet):
    queryset = CustomUser.objects.all()
    serializer_class= UsersSerializers
    
class LoginViewSet(viewsets.ViewSet):
    """
    A simple ViewSet for handling user login.
    """
    def create(self, request):
        serializer = LoginSerializer(data=request.data)
        if serializer.is_valid():
            email = serializer.validated_data['email']
            password = serializer.validated_data['password']
            
            # Authenticate user
            user = authenticate(request, username=email, password=password)
            if user:
                # Create or get token
                token, created = Token.objects.get_or_create(user=user)
                return Response({"token": token.key}, status=status.HTTP_200_OK)
            return Response({"error": "Invalid credentials"}, status=status.HTTP_401_UNAUTHORIZED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)