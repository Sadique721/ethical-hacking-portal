import markdown
import bleach
from django.shortcuts import render, get_object_or_404
from .models import Post

def writeups_list(request):
    posts = Post.objects.all().order_by('-created_at')
    return render(request, 'writeups/writeups_list.html', {'posts': posts})

def writeup_detail(request, pk):
    post = get_object_or_404(Post, pk=pk)
    
    # Render markdown to HTML with code highlighting extensions
    html_content = markdown.markdown(post.content, extensions=['fenced_code', 'codehilite'])
    
    # Define strict whitelist of HTML tags allowed in the rendered Markdown (defend against stored XSS)
    allowed_tags = bleach.ALLOWED_TAGS + [
        'p', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'pre', 'code', 'span', 
        'ul', 'ol', 'li', 'strong', 'em', 'blockquote', 'hr', 'br',
        'table', 'thead', 'tbody', 'tr', 'th', 'td'
    ]
    allowed_attrs = bleach.ALLOWED_ATTRIBUTES.copy()
    allowed_attrs.update({
        'code': ['class'],
        'span': ['class'],
        'pre': ['class'],
    })
    
    sanitized_content = bleach.clean(html_content, tags=allowed_tags, attributes=allowed_attrs)
    
    return render(request, 'writeups/writeup_detail.html', {
        'post': post,
        'content': sanitized_content
    })
