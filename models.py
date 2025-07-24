from django.db import models
from django.contrib.auth.models import User

# Profile Model to store additional user data
class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)  # Link to Django's default User model
    profile_picture = models.ImageField(upload_to='profile_pics/', null=True, blank=True)  # Optional profile picture
    bio = models.TextField(null=True, blank=True)  # Bio or description about the user
    location = models.CharField(max_length=100, null=True, blank=True)  # User's location (optional)

    def __str__(self):
        return f"{self.user.username}'s Profile"

# Contact Model to store contact form submissions
class Contact(models.Model):
    name = models.CharField(max_length=100)
    email = models.EmailField()
    number = models.CharField(max_length=15)  # Phone number (consider using CharField for international numbers)
    desc = models.TextField()  # Description or message
    date = models.DateTimeField(auto_now_add=True)  # Automatically store the date of submission

    def __str__(self):
        return f"Message from {self.name} - {self.email}"

# Optional: You might want to have a model for User Settings or other personalized data
class UserSettings(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    is_newsletter_subscribed = models.BooleanField(default=False)  # Whether the user is subscribed to newsletters
    preferred_language = models.CharField(max_length=50, default='English')  # Preferred language for communication

    def __str__(self):
        return f"Settings for {self.user.username}"
