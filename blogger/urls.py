# blogger/urls.py
from django.urls import path
from . import views

app_name = "blogger"

urlpatterns = [
    path("", views.dashboard, name="dashboard"),
    # lists
    path("text/", views.ContentListView.as_view(type="text"), name="text_list"),
    path("article/", views.ContentListView.as_view(type="article"), name="article_list"),
    path("video/", views.ContentListView.as_view(type="video"), name="video_list"),
    path("poll/", views.ContentListView.as_view(type="poll"), name="poll_list"),
    # create
    path("text/new/", views.create_text, name="text_create"),
    path("article/new/", views.create_article, name="article_create"),
    path("video/new/", views.create_video, name="video_create"),
    path("poll/new/", views.create_poll, name="poll_create"),
    # edit
    path("<int:pk>/edit/", views.edit_content, name="content_edit"),
    # delete
    path("<int:pk>/delete/", views.delete_content, name="content_delete"),
]
