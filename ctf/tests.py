import pytest
import hashlib
from django.contrib.auth.models import User
from django.urls import reverse
from rest_framework.test import APIClient
from MSA.models import Profile
from ctf.models import Challenge, Submission
from audit.models import AuditLog

@pytest.mark.django_db
def test_challenge_flag_verification():
    # Setup flag hash
    flag = "FLAG{sql_injection_master}"
    flag_hash = hashlib.sha256(flag.encode()).hexdigest()
    
    challenge = Challenge.objects.create(
        title="SQL Injection Challenge",
        category="Web Security",
        difficulty="Easy",
        description="Exploit the login page.",
        flag_hash=flag_hash,
        points=100
    )
    
    # Verify correctness checks
    assert challenge.check_flag(flag) is True
    assert challenge.check_flag("FLAG{wrong_flag}") is False


@pytest.mark.django_db
def test_submission_scoring_and_audit():
    user = User.objects.create_user(username="hacker_test", password="testpassword123")
    profile, created = Profile.objects.get_or_create(user=user)
    
    flag = "FLAG{cryptography_is_fun}"
    flag_hash = hashlib.sha256(flag.encode()).hexdigest()
    
    challenge = Challenge.objects.create(
        title="Crypto Basics",
        category="Cryptography",
        difficulty="Easy",
        description="Decrypt this message.",
        flag_hash=flag_hash,
        points=50
    )
    
    # Verify initial points
    assert user.profile.points == 0
    
    # Submit correct flag
    sub = Submission.objects.create(user=user, challenge=challenge, submitted_flag=flag)
    
    assert sub.is_correct is True
    
    # Reload profile from db and verify points are added
    profile.refresh_from_db()
    assert profile.points == 50
    
    # Check that audit log was created
    audit_entry = AuditLog.objects.filter(user=user, action="CTF_SOLVED").first()
    assert audit_entry is not None
    assert "Crypto Basics" in audit_entry.details

    # Submit correct flag again (ensure no double points are awarded)
    sub2 = Submission.objects.create(user=user, challenge=challenge, submitted_flag=flag)
    profile.refresh_from_db()
    assert profile.points == 50  # points must remain 50


@pytest.mark.django_db
def test_ctf_api_endpoints():
    user = User.objects.create_user(username="api_hacker", password="testpassword123")
    profile = Profile.objects.create(user=user)
    
    flag = "FLAG{api_pwned_1337}"
    flag_hash = hashlib.sha256(flag.encode()).hexdigest()
    
    challenge = Challenge.objects.create(
        title="API Security",
        category="Web Security",
        difficulty="Medium",
        description="Audit this API.",
        flag_hash=flag_hash,
        points=75
    )
    
    client = APIClient()
    
    # List challenges (should succeed without auth)
    url = reverse('api-challenges-list')
    response = client.get(url)
    assert response.status_code == 200
    assert len(response.data) == 1
    assert "flag_hash" not in response.data[0] # Verify flag hash is not leaked
    
    # Submit flag (should fail without authentication)
    submit_url = reverse('api-challenges-submit-flag', kwargs={'pk': challenge.id})
    response = client.post(submit_url, {"submitted_flag": flag})
    assert response.status_code == 401
    
    # Authenticate and submit flag
    client.force_authenticate(user=user)
    response = client.post(submit_url, {"submitted_flag": flag})
    assert response.status_code == 201
    assert response.data["message"].startswith("Correct flag!")
    
    # Check points
    profile.refresh_from_db()
    assert profile.points == 75
