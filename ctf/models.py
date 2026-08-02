import hashlib
from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
from MSA.models import Profile

class Challenge(models.Model):
    CATEGORIES = [
        ('Web Security', 'Web Security'),
        ('Network Security', 'Network Security'),
        ('Cryptography', 'Cryptography'),
        ('Reverse Engineering', 'Reverse Engineering'),
        ('Binary Exploitation', 'Binary Exploitation'),
        ('OSINT', 'OSINT'),
    ]

    DIFFICULTIES = [
        ('Easy', 'Easy'),
        ('Medium', 'Medium'),
        ('Hard', 'Hard'),
        ('Insane', 'Insane'),
    ]

    title = models.CharField(max_length=100, unique=True)
    category = models.CharField(max_length=30, choices=CATEGORIES)
    difficulty = models.CharField(max_length=15, choices=DIFFICULTIES)
    description = models.TextField()
    flag_hash = models.CharField(max_length=64, help_text="SHA-256 hash of the flag")
    points = models.IntegerField(default=100)
    hint = models.TextField(null=True, blank=True)

    def __str__(self):
        return f"[{self.category}] {self.title} ({self.points} pts)"

    def check_flag(self, flag_attempt):
        """Hashes the attempt and compares it to the flag hash."""
        attempt_hash = hashlib.sha256(flag_attempt.strip().encode()).hexdigest()
        return attempt_hash == self.flag_hash


class Submission(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='submissions')
    challenge = models.ForeignKey(Challenge, on_delete=models.CASCADE, related_name='submissions')
    submitted_flag = models.CharField(max_length=128)
    is_correct = models.BooleanField(default=False)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        status = "CORRECT" if self.is_correct else "INCORRECT"
        return f"{self.user.username} submitted for {self.challenge.title} - {status}"

    def save(self, *args, **kwargs):
        # Determine if correct before saving
        if not self.pk:  # Only on creation
            self.is_correct = self.challenge.check_flag(self.submitted_flag)
            
            # If correct, check if the user has already solved this challenge
            if self.is_correct:
                already_solved = Submission.objects.filter(
                    user=self.user,
                    challenge=self.challenge,
                    is_correct=True
                ).exists()
                
                if not already_solved:
                    profile, created = Profile.objects.get_or_create(user=self.user)
                    profile.points += self.challenge.points
                    profile.save()
                    
                    # Create an audit log entry (will import inside to avoid circular deps)
                    from audit.models import AuditLog
                    AuditLog.objects.create(
                        user=self.user,
                        action="CTF_SOLVED",
                        details=f"Solved Challenge: {self.challenge.title} (+{self.challenge.points} pts)"
                    )
                else:
                    # Already solved, no extra points awarded
                    pass
            else:
                from audit.models import AuditLog
                AuditLog.objects.create(
                    user=self.user,
                    action="CTF_ATTEMPT_FAILED",
                    details=f"Incorrect attempt for Challenge: {self.challenge.title}"
                )
                
        super().save(*args, **kwargs)
