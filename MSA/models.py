import os
import io
import urllib.parse
from django.db import models
from django.contrib.auth.models import User
from django.core.files.base import ContentFile
from PIL import Image, ImageOps

class Profile(models.Model):
    SKILL_LEVELS = [
        ('Beginner', 'Beginner'),
        ('Intermediate', 'Intermediate'),
        ('Advanced', 'Advanced'),
        ('Expert', 'Expert'),
    ]

    SPECIALIZATIONS = [
        ('Web Security', 'Web Security'),
        ('Network Security', 'Network Security'),
        ('Malware Analysis', 'Malware Analysis'),
        ('Cloud Security', 'Cloud Security'),
        ('OSINT', 'OSINT'),
        ('Cryptography', 'Cryptography'),
        ('Reverse Engineering', 'Reverse Engineering'),
        ('Binary Exploitation', 'Binary Exploitation'),
    ]

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    image = models.ImageField(upload_to='profile_pics/', null=True, blank=True)
    bio = models.TextField(null=True, blank=True)
    location = models.CharField(max_length=100, null=True, blank=True)
    
    # Extended cybersecurity domain fields
    skill_level = models.CharField(max_length=20, choices=SKILL_LEVELS, default='Beginner')
    specialization = models.CharField(max_length=30, choices=SPECIALIZATIONS, default='Web Security')
    github_url = models.URLField(max_length=200, null=True, blank=True)
    linkedin_url = models.URLField(max_length=200, null=True, blank=True)
    certifications = models.TextField(null=True, blank=True, help_text="e.g., OSCP, CEH, CompTIA Security+")
    points = models.IntegerField(default=0)
    is_verified_researcher = models.BooleanField(default=False)
    
    # Custom 2FA secret key
    totp_secret = models.CharField(max_length=32, null=True, blank=True)

    def __str__(self):
        return f"{self.user.username}'s Profile"

    def get_avatar_url(self):
        if self.image:
            return self.image.url
        
        # Generate clean SVG initials fallback
        initials = "".join([c[0] for c in self.user.username.split()[:2]]).upper() or self.user.username[:1].upper()
        svg = f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100" width="100" height="100">
            <rect width="100" height="100" fill="#1e293b"/>
            <text x="50%" y="55%" font-size="40" font-family="'Outfit', sans-serif" font-weight="bold" fill="#38bdf8" dominant-baseline="middle" text-anchor="middle">{initials}</text>
        </svg>"""
        encoded = urllib.parse.quote(svg)
        return f"data:image/svg+xml;utf8,{encoded}"

    def save(self, *args, **kwargs):
        # Image pipeline: strip EXIF data, resize/crop to 512x512 square, convert to WebP
        if self.image:
            try:
                # Open uploaded image
                img = Image.open(self.image)
                
                # Strip EXIF data by loading raw pixel data and recreating the image object
                pixel_data = list(img.getdata())
                clean_img = Image.new(img.mode, img.size)
                clean_img.putdata(pixel_data)
                
                # Fit image to 512x512 square
                clean_img = ImageOps.fit(clean_img, (512, 512), Image.Resampling.LANCZOS)
                
                # Convert and save in WebP format
                output = io.BytesIO()
                clean_img.save(output, format='WEBP', quality=85)
                output.seek(0)
                
                # Generate new WebP filename
                filename = os.path.splitext(self.image.name)[0] + '.webp'
                
                # Save modified image without calling save recursively
                self.image.save(filename, ContentFile(output.read()), save=False)
            except Exception as e:
                # Fallback to saving normally if processing fails
                pass
                
        super().save(*args, **kwargs)


class Contact(models.Model):
    name = models.CharField(max_length=100)
    email = models.EmailField()
    number = models.CharField(max_length=15)
    desc = models.TextField()
    date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Message from {self.name} - {self.email}"


class UserSettings(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    is_newsletter_subscribed = models.BooleanField(default=False)
    preferred_language = models.CharField(max_length=50, default='English')

    def __str__(self):
        return f"Settings for {self.user.username}"
