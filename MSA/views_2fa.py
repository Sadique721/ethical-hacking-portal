import base64
import pyotp
import qrcode
from io import BytesIO
from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from .models import Profile

@login_required
def enable_2fa(request):
    profile, created = Profile.objects.get_or_create(user=request.user)
    
    if profile.totp_secret:
        messages.warning(request, "Two-Factor Authentication is already enabled.")
        return redirect('profile')
        
    if request.method == "POST":
        action = request.POST.get('action')
        if action == 'verify':
            token = request.POST.get('token', '').strip()
            setup_secret = request.session.get('totp_secret_setup')
            
            if not setup_secret:
                messages.error(request, "Setup session expired. Please try again.")
                return redirect('enable_2fa')
                
            totp = pyotp.TOTP(setup_secret)
            if totp.verify(token):
                profile.totp_secret = setup_secret
                profile.save()
                del request.session['totp_secret_setup']
                messages.success(request, "Two-Factor Authentication has been successfully enabled!")
                return redirect('profile')
            else:
                messages.error(request, "Invalid verification code. Please check your authenticator app and try again.")
    
    # Generate fresh secret
    secret = pyotp.random_base32()
    request.session['totp_secret_setup'] = secret
    
    # Generate provisioning URI for authenticator apps
    totp = pyotp.TOTP(secret)
    provisioning_uri = totp.provisioning_uri(
        name=request.user.username, 
        issuer_name="Ethical Hacking Portal"
    )
    
    # Generate QR Code image
    qr = qrcode.QRCode(version=1, box_size=8, border=4)
    qr.add_data(provisioning_uri)
    qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="white")
    
    buffer = BytesIO()
    img.save(buffer, format="PNG")
    qr_base64 = base64.b64encode(buffer.getvalue()).decode()
    qr_code_url = f"data:image/png;base64,{qr_base64}"
    
    return render(request, "enable_2fa.html", {
        "secret": secret,
        "qr_code_url": qr_code_url
    })

@login_required
def disable_2fa(request):
    profile, created = Profile.objects.get_or_create(user=request.user)
    if not profile.totp_secret:
        messages.warning(request, "Two-Factor Authentication is not enabled.")
        return redirect('profile')
        
    if request.method == "POST":
        profile.totp_secret = None
        profile.save()
        messages.success(request, "Two-Factor Authentication has been disabled.")
        return redirect('profile')
        
    return render(request, "disable_2fa.html")

def verify_2fa(request):
    user_id = request.session.get('pre_2fa_user_id')
    if not user_id:
        return redirect('login')
        
    try:
        user = User.objects.get(id=user_id)
    except User.DoesNotExist:
        return redirect('login')
        
    if request.method == "POST":
        token = request.POST.get('token', '').strip()
        profile = user.profile
        
        totp = pyotp.TOTP(profile.totp_secret)
        if totp.verify(token):
            login(request, user)
            del request.session['pre_2fa_user_id']
            messages.success(request, "Login verification successful!")
            return redirect('dashboard')
        else:
            messages.error(request, "Invalid verification code.")
            
    return render(request, "verify_2fa.html", {"username": user.username})
