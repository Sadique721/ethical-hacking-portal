from django.shortcuts import render, HttpResponse
from datetime import datetime
from MSA.models import Contact
from django.contrib import messages
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib import messages
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .forms import RegisterForm, EditProfileForm
from MSA.models import Profile

@login_required
def profile(request):
    profile, created = Profile.objects.get_or_create(user=request.user)
    return render(request, 'profile.html', {'profile': profile})

# User Registration View
def registers(request):
    if request.method == "POST":
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)  # Automatically log in the user after registration
            messages.success(request, "Registration successful!")
            return redirect('profile')  # Redirect to profile page
        else:
            messages.error(request, "Error in registration. Please check your inputs.")
    else:
        form = RegisterForm()

    return render(request, 'registers.html', {'form': form})

# User Profile View
@login_required
def profile(request):
    return render(request, 'profile.html', {'user': request.user})

# Edit Profile View
@login_required
def edit_profile(request):
    if request.method == "POST":
        form = EditProfileForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, "Profile updated successfully!")
            return redirect('profile')
    else:
        form = EditProfileForm(instance=request.user)

    return render(request, 'edit_profile.html', {'form': form})

@login_required(login_url='login')  # Redirects to login if user is not authenticated
def dashboard(request):
    return render(request, "dashboard.html")

@login_required(login_url='login')
def user_profile(request):
    return render(request, "profile.html")


def user_login(request):
    if request.method == "POST":
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            messages.success(request, "Login successful!")
            return redirect("MSA")  # Redirect to home page
        else:
            messages.error(request, "Invalid username or password!")
    return render(request, "login.html")

def user_register(request):
    if request.method == "POST":
        username = request.POST["username"]
        email = request.POST["email"]
        password1 = request.POST["password1"]
        password2 = request.POST["password2"]

        if password1 == password2:
            if User.objects.filter(username=username).exists():
                messages.error(request, "Username already taken!")
            elif User.objects.filter(email=email).exists():
                messages.error(request, "Email already registered!")
            else:
                user = User.objects.create_user(username=username, email=email, password=password1)
                user.save()
                messages.success(request, "Registration successful! Please log in.")
                return redirect("login")
        else:
            messages.error(request, "Passwords do not match!")
    
    return render(request, "register.html")

def user_logout(request):
    logout(request)
    messages.success(request, "You have been logged out!")
    return redirect("login")


# Create your views here.
def index(request):
    context = {
        'variable1': "seven two one",
        'variable2': "seven two nine"
    }
    return render(request, 'index.html')
   # return HttpResponse("this is home page")

def about(request):
     return render(request, 'about.html')
    #return HttpResponse("this is about page")


def services(request):
      return render(request, 'services.html')
   # return HttpResponse("this is  services page")

def contact(request):
      if request.method == "POST":
           name = request.POST.get('name')
           email = request.POST.get('email')
           number = request.POST.get('number')
           desc = request.POST.get('desc')
           contact = Contact(name=name, email=email, number=number, desc=desc, date=datetime.today())
           contact.save()
           messages.success(request, "Your details successfully submited!")
      return render(request, 'contact.html')
    #return HttpResponse("this is contact page")