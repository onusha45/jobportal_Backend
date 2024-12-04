from django.contrib import admin
from django.urls import path,include
from django.conf import settings
from django.conf.urls.static import static
from rest_framework.routers import DefaultRouter
from User_app.views import *
from .user_viewset import UsersViewsets,LoginViewSet
from rest_framework_simplejwt.views import (
    TokenObtainPairView, 
    TokenRefreshView,    
)

router = DefaultRouter()
router.register('users',UsersViewsets,basename='UsersViewsets')
router.register('login', LoginViewSet, basename='login')

urlpatterns =   [
     path('signup/', signup ,name='signup'),
     path('employer_signup', employer_signup, name="employer_signup"),
     path('jobseeker_signup', jobseeker_signup, name="jobseeker_signup"),
     path('login/',login,name='login'),
     path('jobseekerhome/', jobseekerhome ,name='jobseekerhome'),
     path('employerhome/', employerhome ,name='employerhome'),
     path('api/',include(router.urls)),
    
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)