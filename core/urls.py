from django.urls import path
from . import views

urlpatterns = [
    path("", views.home, name="home"),
    path("content/", views.content_list, name="content_list"),
    path("content/<int:pk>/", views.content_detail, name="content_detail"),
]
