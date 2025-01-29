from django.shortcuts import render
from rest_framework.response import Response
from rest_framework import status
from rest_framework.generics import ListCreateAPIView
from rest_framework.permissions import IsAuthenticated
from .serializers import JobApplySerializer
from accounts.models import JobApply, JobPosting, CustomUser

class CreateJobApiView(ListCreateAPIView):
   
    queryset = JobApply.objects.all()
    serializer_class = JobApplySerializer

    def post(self, request, *args, **kwargs):
        try:
            job = JobPosting.objects.get(id=kwargs['id']) 
        except JobPosting.DoesNotExist:
            return Response({"error": "Job posting not found."}, status=status.HTTP_404_NOT_FOUND)

        try:
            user = CustomUser.objects.get(id=request.user.id)
        except CustomUser.DoesNotExist:
            return Response({"error" : "User not found."}, status=status.HTTP_404_NOT_FOUND)

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        job_application = serializer.save(user=user, job=job)  
        return Response(JobApplySerializer(job_application).data, status=status.HTTP_201_CREATED)

