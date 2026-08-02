import pytest
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.core.files.uploadedfile import SimpleUploadedFile
from MSA.models import Profile
from MSA.forms import EditProfileForm

@pytest.mark.django_db
def test_profile_svg_avatar_generation():
    user = User.objects.create_user(username="Alice Cyber", password="testpassword123")
    profile, created = Profile.objects.get_or_create(user=user)
    
    # Assert that no image exists initially
    assert not profile.image
    
    # Fetch initials avatar URL
    avatar_url = profile.get_avatar_url()
    assert avatar_url.startswith("data:image/svg+xml;utf8,")
    assert "AC" in avatar_url # Initials for Alice Cyber
    
    # Try with single word username
    user2 = User.objects.create_user(username="bob", password="testpassword123")
    profile2 = Profile.objects.create(user=user2)
    avatar_url2 = profile2.get_avatar_url()
    assert "B" in avatar_url2


@pytest.mark.django_db
def test_profile_form_file_validation():
    user = User.objects.create_user(username="malicious_uploader", password="testpassword123")
    profile = Profile.objects.create(user=user)
    
    # 1. Test invalid file extension (.txt instead of image)
    invalid_file = SimpleUploadedFile(
        "exploit.txt", 
        b"<?php system($_GET['cmd']); ?>", 
        content_type="text/plain"
    )
    form = EditProfileForm(
        data={'bio': 'Testing exploit upload', 'location': 'Localhost'},
        files={'image': invalid_file},
        instance=profile
    )
    assert form.is_valid() is False
    assert "image" in form.errors
    assert any(msg in form.errors["image"][0] for msg in ["Unsupported file extension", "Upload a valid image"])
    
    # 2. Test file size validation (file size > 2MB)
    large_data = b"0" * (2 * 1024 * 1024 + 100) # 2MB + 100 bytes
    large_file = SimpleUploadedFile(
        "heavy.png",
        large_data,
        content_type="image/png"
    )
    form2 = EditProfileForm(
        data={'bio': 'Testing heavy upload', 'location': 'Localhost'},
        files={'image': large_file},
        instance=profile
    )
    assert form2.is_valid() is False
    assert "image" in form2.errors
    assert any(msg in form2.errors["image"][0] for msg in ["file size cannot exceed 2MB", "Upload a valid image"])
