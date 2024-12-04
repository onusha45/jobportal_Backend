from django.shortcuts import render,redirect
from .forms import EmployeerSignup
from .models import CustomUser
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from rest_framework.authtoken.models import Token 
from django.contrib.auth import authenticate

from rest_framework.authtoken.views import ObtainAuthToken 


@csrf_exempt
def gettoken(request):
    if request.method == 'POST':
        # Assuming you have a user authentication system in place:
        username = request.POST.get('username')
        password = request.POST.get('password')

        # Authenticate the user
        user = authenticate(username=username, password=password)

        if user is not None and user.is_active:
            token, created = Token.objects.get_or_create(user=user)
            return JsonResponse({'token': token.key})
        else:
            return JsonResponse({'error': 'Invalid credentials'}, status=401) 

    else:
        return JsonResponse({'error': 'Method Not Allowed'}, status=405) 


def employerhome(request):
    return render(request, "employerhome.html")


def employer_signup(request):
    if request.method == "POST":
        form = EmployeerSignup(request.POST)
        if form.is_valid():
            user_id = request.session.get('user_id')
            if not user_id:
                return redirect('signup')
            user = CustomUser.objects.get(pk=user_id)
            user.phone_no = form.cleaned_data['phone_no']
            user.address = form.cleaned_data['address']
            user.company_name = form.cleaned_data['company_name']
            user.pan_no = form.cleaned_data['pan_no']
            user.save()

            del request.session['user_id']

            return redirect('login')
        else:
            print("Form errors:", form.errors)
    else:
        form = EmployeerSignup()
        context = {
            'form':form,

        }
    return render(request, 'employersignup.html',context)