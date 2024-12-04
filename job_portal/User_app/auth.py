from django.shortcuts import render,redirect
from django.contrib.auth import authenticate ,login as auth_login
from rest_framework_simplejwt.tokens import AccessToken
from .forms import Login,UserSignup
from django.http import JsonResponse

def signup(request):
    if request.method == "POST":
        form = UserSignup(request.POST, request.FILES)
        if form.is_valid():
            user = form.save(commit=False)
            
            password = form.cleaned_data.get('password')
            confirm_password = form.cleaned_data.get('repassword')
            is_Employeer = form.cleaned_data.get('isEmployer')
            
            
            if password != confirm_password:
                form.add_error('repassword', 'Passwords do not match.')
            else:
                user.set_password(password)
                user.save()
                if(is_Employeer):
                    request.session["user_id"] = user.id
                    return redirect('employer_signup')
                else:
                    request.session["user_id"] = user.id
                    return redirect('jobseeker_signup')
        else:
            print(form.errors)
            print(request.FILES)
            print(request.POST)
    else:
        form = UserSignup()
        
    context = {
        'form': form,
    }
    
    return render(request, 'signup.html', context)






        


def login(request):
    if request.method == 'POST':
        form = Login(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            
            user = authenticate(request, username=username, password=password)
            if user is not None:

                '''
                Session Based Authentication
                '''
                auth_login(request, user)
                print(user.isEmployer)
                if user.isEmployer:
                    print("emp")
                    return redirect('employerhome')
                else:
                    print("jobseek")
                    return redirect('jobseekerhome') 

                '''
                JWT Based Authentication
                '''
                # access_token = AccessToken.for_user(user)

                # return JsonResponse({
                #     'access': str(access_token),
                # }, status=200)
                
            else:
                form.add_error(None, 'Invalid email or password.')
        else:
            print("Not valid")
    else:
        form = Login()
        
    context = {
        'form': form
    }
    
    return render(request, 'login.html', context)