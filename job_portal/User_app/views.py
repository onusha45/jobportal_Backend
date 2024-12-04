from .models import CustomUser
# --------------- Employer Views -------------------#
from .employer_views import *
# --------------- JobSeeker Views -------------------#
from .jobseeker import *
# --------------- Auth Views -------------------#
from .auth import *

from rest_framework_simplejwt.views import TokenObtainPairView
from User_app.serializers import CustomTokenObtainPairSerializer

class CustomTokenObtainPairView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer






