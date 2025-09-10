# blogger/views.py
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render
from django.utils.decorators import method_decorator
from django.views.generic import ListView

from core.models import Content, Poll
from .forms import (
    TextContentForm, ArticleContentForm, VideoContentForm,
    PollContentForm, PollForm, PollOptionFormSet
)

@login_required
def dashboard(request):
    counts = {
        "text": Content.objects.filter(content_type="text").count(),
        "article": Content.objects.filter(content_type="article").count(),
        "video": Content.objects.filter(content_type="video").count(),
        "poll": Content.objects.filter(content_type="poll").count(),
    }
    return render(request, "blogger/dashboard.html", {"counts": counts})

@method_decorator(login_required, name="dispatch")
class ContentListView(ListView):
    model = Content
    template_name = "blogger/content_list.html"
    context_object_name = "items"
    paginate_by = 12
    type = None

    def get_queryset(self):
        ctype = getattr(self, "type") or self.kwargs.get("type") or self.request.GET.get("type")
        qs = Content.objects.all().order_by("-created_at")
        if ctype:
            qs = qs.filter(content_type=ctype)
        return qs

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctype = getattr(self, "type") or self.request.GET.get("type")
        ctx["ctype"] = ctype
        return ctx

@login_required
def create_text(request):
    if request.method == "POST":
        form = TextContentForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, "Text tip created.")
            return redirect("blogger:text_list")
    else:
        form = TextContentForm()
    return render(request, "blogger/content_form.html", {"form": form, "title": "New Text Tip", "ctype": "text"})

@login_required
def create_article(request):
    if request.method == "POST":
        form = ArticleContentForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, "Article created.")
            return redirect("blogger:article_list")
    else:
        form = ArticleContentForm()
    return render(request, "blogger/content_form.html", {"form": form, "title": "New Article", "ctype": "article"})

@login_required
def create_video(request):
    if request.method == "POST":
        form = VideoContentForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, "Video post created.")
            return redirect("blogger:video_list")
    else:
        form = VideoContentForm()
    return render(request, "blogger/content_form.html", {"form": form, "title": "New Video", "ctype": "video"})

@login_required
def create_poll(request):
    if request.method == "POST":
        cform = PollContentForm(request.POST)
        pform = PollForm(request.POST)
        if cform.is_valid() and pform.is_valid():
            content = cform.save()
            poll = pform.save(commit=False)
            poll.content = content
            poll.save()
            formset = PollOptionFormSet(request.POST, instance=poll)
            if formset.is_valid():
                formset.save()
                messages.success(request, "Poll created.")
                return redirect("blogger:poll_list")
        else:
            # rebind formset too for errors
            dummy_poll = Poll(content=Content(content_type="poll"))
            formset = PollOptionFormSet(request.POST, instance=dummy_poll)
    else:
        cform = PollContentForm()
        pform = PollForm()
        formset = PollOptionFormSet()
    return render(request, "blogger/poll_form.html", {
        "cform": cform, "pform": pform, "formset": formset, "title": "New Poll", "ctype": "poll"
    })

@login_required
def edit_content(request, pk):
    obj = get_object_or_404(Content, pk=pk)
    if obj.content_type == "text":
        FormClass = TextContentForm
        template = "blogger/content_form.html"
        ctx = {"title": f"Edit Text: {obj.title}", "ctype": "text"}
        if request.method == "POST":
            form = FormClass(request.POST, request.FILES, instance=obj)
            if form.is_valid():
                form.save()
                messages.success(request, "Text updated.")
                return redirect("blogger:text_list")
        else:
            form = FormClass(instance=obj)
        ctx["form"] = form
        return render(request, template, ctx)

    if obj.content_type == "article":
        FormClass = ArticleContentForm
        template = "blogger/content_form.html"
        ctx = {"title": f"Edit Article: {obj.title}", "ctype": "article"}
        if request.method == "POST":
            form = FormClass(request.POST, request.FILES, instance=obj)
            if form.is_valid():
                form.save()
                messages.success(request, "Article updated.")
                return redirect("blogger:article_list")
        else:
            form = FormClass(instance=obj)
        ctx["form"] = form
        return render(request, template, ctx)

    if obj.content_type == "video":
        FormClass = VideoContentForm
        template = "blogger/content_form.html"
        ctx = {"title": f"Edit Video: {obj.title}", "ctype": "video"}
        if request.method == "POST":
            form = FormClass(request.POST, request.FILES, instance=obj)
            if form.is_valid():
                form.save()
                messages.success(request, "Video updated.")
                return redirect("blogger:video_list")
        else:
            form = FormClass(instance=obj)
        ctx["form"] = form
        return render(request, template, ctx)

    if obj.content_type == "poll":
        poll = getattr(obj, "poll", None)
        if poll is None:
            poll = Poll.objects.create(content=obj, question="")
        if request.method == "POST":
            cform = PollContentForm(request.POST, instance=obj)
            pform = PollForm(request.POST, instance=poll)
            formset = PollOptionFormSet(request.POST, instance=poll)
            if cform.is_valid() and pform.is_valid() and formset.is_valid():
                cform.save()
                pform.save()
                formset.save()
                messages.success(request, "Poll updated.")
                return redirect("blogger:poll_list")
        else:
            cform = PollContentForm(instance=obj)
            pform = PollForm(instance=poll)
            formset = PollOptionFormSet(instance=poll)
        return render(request, "blogger/poll_form.html", {
            "cform": cform, "pform": pform, "formset": formset, "title": f"Edit Poll: {obj.title}", "ctype": "poll"
        })

    messages.error(request, "Unsupported content type.")
    return redirect("blogger:dashboard")

@login_required
def delete_content(request, pk):
    obj = get_object_or_404(Content, pk=pk)
    if request.method == "POST":
        obj.delete()
        messages.success(request, "Deleted successfully.")
        # redirect to the correct list
        return redirect(f"blogger:{obj.content_type}_list")
    return render(request, "blogger/confirm_delete.html", {"object": obj})
