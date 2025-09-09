from django.db import models
from django.urls import reverse

class Content(models.Model):
    CONTENT_TYPES = [
        ("text", "Text Update"),
        ("article", "Article"),
        ("image", "Image"),
        ("video", "Video"),
        ("poll", "Poll"),
    ]

    title = models.CharField(max_length=255)
    content_type = models.CharField(max_length=20, choices=CONTENT_TYPES)
    excerpt = models.TextField(blank=True, null=True)  # short preview for cards
    body = models.TextField(blank=True, null=True)     # full text/article content
    image = models.ImageField(upload_to="images/", blank=True, null=True)
    thumbnail = models.ImageField(upload_to="thumbnails/", blank=True, null=True)
    video_url = models.URLField(blank=True, null=True) # for YouTube/Vimeo links
    created_at = models.DateTimeField(auto_now_add=True)
    view_count = models.PositiveIntegerField(default=0)
    is_featured = models.BooleanField(default=False)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.title} ({self.content_type})"

    def get_absolute_url(self):
        return reverse("content_detail", args=[str(self.id)])


class Poll(models.Model):
    content = models.OneToOneField(
        Content, on_delete=models.CASCADE, related_name="poll"
    )
    question = models.CharField(max_length=255)

    def __str__(self):
        return self.question


class PollOption(models.Model):
    poll = models.ForeignKey(Poll, on_delete=models.CASCADE, related_name="options")
    option_text = models.CharField(max_length=255)
    votes = models.PositiveIntegerField(default=0)

    def __str__(self):
        return self.option_text

