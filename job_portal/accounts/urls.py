from django.urls import path

from .views import JobApplicantDetailView, SignupView, LoginView, UserDetailsView, JobPostingView, ProfileView, ResumeUploadView
from .views import RecommendedJobsView, ApplyJobView, JobApplicationView, EmployerProfileView, ListJobViewApi
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)

urlpatterns = [
    path('signup/', SignupView.as_view(), name="signup"),
    path('login/', LoginView.as_view(), name='login'),

    path('jobposting/', JobPostingView.as_view(), name="jobposting"),

    # utsab
    path('upload-resume/', ResumeUploadView.as_view(), name='upload_resume'),

    path('profile/', ProfileView.as_view(), name='profile'),
    path('employer-profile/', EmployerProfileView.as_view(), name='employer_profile'),

    path('user-details/', UserDetailsView.as_view(), name='user_details'),  # changes made my utsab
    path('token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('recommended-jobs/', RecommendedJobsView.as_view(), name='recommended_jobs'),  # utsab
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('apply-job/', JobApplicationView.as_view(), name='apply-job'),
    path('applicant/<int:job_id>/', JobApplicantDetailView.as_view()),
    path('jobs/posted/', ListJobViewApi.as_view())

]
