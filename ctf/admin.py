from django.contrib import admin
from .models import Challenge, Submission

@admin.register(Challenge)
class ChallengeAdmin(admin.ModelAdmin):
    list_display = ('title', 'category', 'difficulty', 'points')
    list_filter = ('category', 'difficulty')
    search_fields = ('title', 'description')

@admin.register(Submission)
class SubmissionAdmin(admin.ModelAdmin):
    list_display = ('user', 'challenge', 'submitted_flag', 'is_correct', 'timestamp')
    list_filter = ('is_correct', 'timestamp')
    search_fields = ('user__username', 'challenge__title', 'submitted_flag')
    readonly_fields = ('timestamp',)
