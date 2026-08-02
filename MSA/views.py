from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from datetime import datetime
from .models import Contact, Profile
from .forms import RegisterForm, EditUserForm, EditProfileForm

@login_required
def profile(request):
    # Ensure profile exists, then render
    profile_obj, created = Profile.objects.get_or_create(user=request.user)
    return render(request, 'profile.html', {'profile': profile_obj})

@login_required
def edit_profile(request):
    profile_obj, created = Profile.objects.get_or_create(user=request.user)
    if request.method == "POST":
        user_form = EditUserForm(request.POST, instance=request.user)
        profile_form = EditProfileForm(request.POST, request.FILES, instance=profile_obj)
        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            profile_form.save()
            messages.success(request, "Profile updated successfully!")
            return redirect('profile')
        else:
            messages.error(request, "Please correct the errors below.")
    else:
        user_form = EditUserForm(instance=request.user)
        profile_form = EditProfileForm(instance=profile_obj)

    return render(request, 'edit_profile.html', {
        'user_form': user_form,
        'profile_form': profile_form,
        'profile': profile_obj
    })

@login_required(login_url='login')
def dashboard(request):
    from ctf.models import Challenge, Submission
    from audit.models import AuditLog
    
    profile_obj = request.user.profile
    total_challenges = Challenge.objects.count()
    solved_count = Submission.objects.filter(user=request.user, is_correct=True).count()
    
    # Calculate Rank
    user_points = profile_obj.points
    rank = Profile.objects.filter(points__gt=user_points).count() + 1
    
    # Fetch recent audit logs
    logs = AuditLog.objects.filter(user=request.user).order_by('-timestamp')[:5]
    
    # Prepare statistics for charts (e.g. challenges category breakdown)
    # Get solved counts by category
    categories = [cat[0] for cat in Challenge.CATEGORIES]
    solved_by_cat = []
    total_by_cat = []
    
    for cat in categories:
        total_by_cat.append(Challenge.objects.filter(category=cat).count())
        solved_by_cat.append(Submission.objects.filter(user=request.user, challenge__category=cat, is_correct=True).count())
    
    context = {
        'total_challenges': total_challenges,
        'solved_count': solved_count,
        'points': user_points,
        'rank': rank,
        'recent_logs': logs,
        'categories': categories,
        'solved_by_cat': solved_by_cat,
        'total_by_cat': total_by_cat,
    }
    return render(request, "dashboard.html", context)

def user_login(request):
    if request.user.is_authenticated:
        return redirect('dashboard')
        
    if request.method == "POST":
        username = request.POST.get("username", "").strip()
        password = request.POST.get("password", "")
        
        user = authenticate(request, username=username, password=password)
        if user is not None:
            # Check if user has TOTP 2FA enabled
            profile_obj, created = Profile.objects.get_or_create(user=user)
            if profile_obj.totp_secret:
                # Store user ID in session temporarily, redirect to 2FA page
                request.session['pre_2fa_user_id'] = user.id
                messages.info(request, "Two-Factor Authentication is required.")
                return redirect('verify_2fa')
            
            # Standard login
            login(request, user)
            messages.success(request, "Login successful!")
            return redirect("dashboard")
        else:
            messages.error(request, "Invalid username or password!")
            
    return render(request, "login.html")

def user_register(request):
    if request.user.is_authenticated:
        return redirect('dashboard')

    if request.method == "POST":
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            # Ensure profile object is created automatically
            Profile.objects.create(user=user)
            
            messages.success(request, "Registration successful! Please log in.")
            return redirect("login")
        else:
            messages.error(request, "Error in registration. Please check your inputs.")
    else:
        form = RegisterForm()
        
    return render(request, "register.html", {'form': form})

def user_logout(request):
    logout(request)
    messages.success(request, "You have been logged out!")
    return redirect("login")

def index(request):
    return render(request, 'index.html')

def about(request):
    # Retrieve top researchers for public stats
    top_researchers = Profile.objects.select_related('user').order_by('-points')[:4]
    return render(request, 'about.html', {'top_researchers': top_researchers})

def services(request):
    return render(request, 'services.html')

def contact(request):
    if request.method == "POST":
        name = request.POST.get('name')
        email = request.POST.get('email')
        number = request.POST.get('number')
        desc = request.POST.get('desc')
        contact_obj = Contact(name=name, email=email, number=number, desc=desc, date=datetime.today())
        contact_obj.save()
        messages.success(request, "Your details were successfully submitted!")
    return render(request, 'contact.html')