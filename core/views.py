from django.shortcuts import render, get_object_or_404
from django.db.models import Count
from .models import Content

def home(request):
    featured_posts = Content.objects.filter(is_featured=True)[:3]
    post_list = Content.objects.all()[:10]
    total_count = Content.objects.count()

    # Count by type
    counts = Content.objects.values("content_type").annotate(total=Count("id"))
    type_counts = {c["content_type"]: c["total"] for c in counts}

    context = {
        "featured_posts": featured_posts,
        "post_list": post_list,
        "total_count": total_count,
        "subscriber_count": 1200,  # Replace with real data from WhatsApp API
        "text_count": type_counts.get("text", 0),
        "article_count": type_counts.get("article", 0),
        "image_count": type_counts.get("image", 0),
        "video_count": type_counts.get("video", 0),
        "poll_count": type_counts.get("poll", 0),
    }
    return render(request, "home.html", context)

def content_list(request):
    post_list = Content.objects.all()
    return render(request, "content_list.html", {"post_list": post_list})

def content_detail(request, pk):
    content = get_object_or_404(Content, pk=pk)

    # Update view count
    content.view_count += 1
    content.save(update_fields=["view_count"])

    # For polls, we may need options
    poll = getattr(content, "poll", None)

    context = {
        "content": content,
        "poll": poll,
        "total_votes": 200, 
    }
    return render(request, "content_detail.html", context)