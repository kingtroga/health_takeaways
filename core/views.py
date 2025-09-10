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

# core/views.py
from django.shortcuts import render
from django.db.models import Q
from django.core.paginator import Paginator
from .models import Content

def content_list(request):
    ctype = (request.GET.get("type") or "").strip().lower()
    allowed = {key for key, _ in Content.CONTENT_TYPES}

    qs = Content.objects.all()
    if ctype in allowed:
        qs = qs.filter(content_type=ctype)

    # (Optional) basic search support: ?q=...
    q = (request.GET.get("q") or "").strip()
    if q:
        qs = qs.filter(
            Q(title__icontains=q) |
            Q(excerpt__icontains=q) |
            Q(body__icontains=q)
        )

    # Pagination (adjust per page as you like)
    paginator = Paginator(qs, 12)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    context = {
        "post_list": page_obj.object_list,
        "page_obj": page_obj,
        "is_paginated": page_obj.has_other_pages(),
        "ctype": ctype or None,   # <-- use this in template instead of request.GET.type
        "q": q,
    }
    return render(request, "content_list.html", context)


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