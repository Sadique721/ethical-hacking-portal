from django.contrib import admin
from .models import Contact, Profile, UserSettings

# Register your models here.

admin.site.register(Contact)
admin.site.register(Profile)
admin.site.register(UserSettings)
