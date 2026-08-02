from rest_framework import serializers
from .models import Challenge, Submission

class ChallengeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Challenge
        # Exclude flag_hash to ensure security!
        fields = ['id', 'title', 'category', 'difficulty', 'description', 'points', 'hint']

class SubmissionSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source='user.username', read_only=True)
    challenge_title = serializers.CharField(source='challenge.title', read_only=True)

    class Meta:
        model = Submission
        fields = ['id', 'username', 'challenge', 'challenge_title', 'submitted_flag', 'is_correct', 'timestamp']
        read_only_fields = ['is_correct', 'timestamp']
