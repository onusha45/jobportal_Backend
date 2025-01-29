from django.urls import path
from .views import CreateJobApiView

urlpatterns = [
    path('apply/<int:id>/', CreateJobApiView.as_view(), name="upload_file"),
]   