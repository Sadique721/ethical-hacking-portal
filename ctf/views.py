from django.shortcuts import render, redirect
from django.shortcuts import get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import HttpResponse, JsonResponse
from django.db.models import Count, Q
from django_ratelimit.decorators import ratelimit
from MSA.models import Profile
from .models import Challenge, Submission

@login_required
def challenges_list(request):
    challenges = Challenge.objects.all().order_by('category', 'points')
    
    # Annotate with whether user solved it
    user_submissions = Submission.objects.filter(user=request.user, is_correct=True)
    solved_challenge_ids = set(user_submissions.values_list('challenge_id', flat=True))
    
    for challenge in challenges:
        challenge.solved_by_user = challenge.id in solved_challenge_ids
        
    return render(request, 'ctf/challenges.html', {
        'challenges': challenges,
        'solved_ids': solved_challenge_ids
    })

@login_required
@ratelimit(key='user', rate='5/m', method='POST', block=False)
def submit_flag(request, challenge_id):
    # Check if rate-limited
    was_limited = getattr(request, 'limited', False)
    if was_limited:
        if request.headers.get('HX-Request'):
            return HttpResponse(
                '<div class="alert alert-danger font-monospace">RATE_LIMIT_EXCEEDED: Max 5 attempts per minute.</div>',
                status=429
            )
        messages.error(request, "Too many attempts. Please wait a minute.")
        return redirect('challenge_detail', pk=challenge_id)

    challenge = get_object_or_404(Challenge, id=challenge_id)
    
    if request.method == "POST":
        flag = request.POST.get('flag', '').strip()
        
        # Check if already solved
        already_solved = Submission.objects.filter(
            user=request.user, 
            challenge=challenge, 
            is_correct=True
        ).exists()
        
        if already_solved:
            if request.headers.get('HX-Request'):
                return HttpResponse('<div class="alert alert-warning font-monospace">ALREADY_SOLVED: You have already captured this flag!</div>')
            messages.warning(request, "You have already solved this challenge!")
            return redirect('challenges_list')
            
        submission = Submission(user=request.user, challenge=challenge, submitted_flag=flag)
        submission.save()  # This computes correctness and awards points
        
        if submission.is_correct:
            response_html = f"""
            <div class="alert alert-success font-monospace mb-0">
                <i class="bi bi-trophy-fill"></i> FLAG_CAPTURED! +{challenge.points} Points.
            </div>
            <script nonce="{request.csp_nonce}">
                document.getElementById('challenge-card-{challenge.id}').classList.add('border-success');
                document.getElementById('badge-{challenge.id}').className = 'badge bg-success';
                document.getElementById('badge-{challenge.id}').innerText = 'SOLVED';
            </script>
            """
            if request.headers.get('HX-Request'):
                return HttpResponse(response_html)
            messages.success(request, "Correct flag! Points added.")
            return redirect('challenges_list')
        else:
            response_html = """
            <div class="alert alert-danger font-monospace mb-0">
                <i class="bi bi-x-circle-fill"></i> INVALID_FLAG. Access Denied.
            </div>
            """
            if request.headers.get('HX-Request'):
                return HttpResponse(response_html)
            messages.error(request, "Incorrect flag. Try again.")
            
    return redirect('challenges_list')

def leaderboard(request):
    profiles = Profile.objects.select_related('user').order_by('-points', 'user__username')
    return render(request, 'ctf/leaderboard.html', {'profiles': profiles})
