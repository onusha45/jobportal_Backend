
from django.shortcuts import render,redirect
from .forms import JobseekerSignup
from .models import CustomUser


def jobseekerhome(request ):
   user = request.user
   context = {
       'user':user,
   }
   return render(request,'jobseekerhome.html',context)


def jobseeker_signup(request):
    if request.method == "POST":
        form = JobseekerSignup(request.POST)
        if form.is_valid():
            user_id = request.session.get('user_id')
            if not user_id:
                return redirect('signup')
            user = CustomUser.objects.get(pk=user_id)
            user.phone_no = form.cleaned_data['phone_no']
            user.address = form.cleaned_data['address']
            user.qualification = form.cleaned_data['qualification']
            user.first_name = form.cleaned_data['first_name']
            user.last_name = form.cleaned_data['last_name']          
            user.resume = form.cleaned_data['resume']          
            user.save()

            del request.session['user_id']

            return redirect('login')
        else:
            print("Form errors:", form.errors)
    else:
        form = JobseekerSignup()
        context = {
            'form':form,

        }
    return render(request, 'jobseekersignup.html',context)