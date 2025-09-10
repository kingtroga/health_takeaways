from django import forms
from django.forms import inlineformset_factory
from core.models import Content, Poll, PollOption

# ---------- Tailwind mixin ----------

INPUT_CSS = (
    "block w-full rounded-lg border border-gray-300 bg-white px-3 py-2 "
    "text-gray-900 placeholder-gray-400 shadow-sm "
    "focus:border-health-primary focus:ring-2 focus:ring-health-primary/50 sm:text-sm"
)
TEXTAREA_CSS = (
    "block w-full rounded-lg border border-gray-300 bg-white px-3 py-2 "
    "text-gray-900 placeholder-gray-400 shadow-sm "
    "focus:border-health-primary focus:ring-2 focus:ring-health-primary/50 sm:text-sm"
)
FILE_CSS = (
    "block w-full text-sm text-gray-900 "
    "file:mr-4 file:py-2 file:px-4 file:rounded-md file:border-0 "
    "file:font-medium file:bg-gray-100 file:text-gray-700 hover:file:bg-gray-200"
)
CHECKBOX_CSS = "h-4 w-4 rounded border-gray-300 text-health-primary focus:ring-health-primary"
SELECT_CSS = (
    "block w-full rounded-lg border border-gray-300 bg-white px-3 py-2 "
    "text-gray-900 shadow-sm focus:border-health-primary focus:ring-2 "
    "focus:ring-health-primary/50 sm:text-sm"
)

class TailwindFormMixin:
    """
    Auto-apply Tailwind classes to widgets.
    Works with your existing template loop: {{ field.label }} then {{ field }} then {{ field.errors }}
    """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        for name, field in self.fields.items():
            w = field.widget
            # Base classes by widget type
            if isinstance(w, (forms.TextInput, forms.EmailInput, forms.URLInput,
                              forms.NumberInput, forms.PasswordInput)):
                w.attrs.setdefault("class", INPUT_CSS)
                w.attrs.setdefault("placeholder", field.label)
            elif isinstance(w, forms.Textarea):
                w.attrs.setdefault("class", TEXTAREA_CSS)
                w.attrs.setdefault("rows", 8 if name == "body" else 4)
                w.attrs.setdefault("placeholder", field.label)
            elif isinstance(w, forms.ClearableFileInput):
                w.attrs.setdefault("class", FILE_CSS)
                if name in {"image", "thumbnail"}:
                    w.attrs.setdefault("accept", "image/*")
            elif isinstance(w, forms.CheckboxInput):
                w.attrs.setdefault("class", CHECKBOX_CSS)
            elif isinstance(w, (forms.Select, forms.SelectMultiple)):
                w.attrs.setdefault("class", SELECT_CSS)

            # Nice placeholders for specific fields
            if name == "title":
                w.attrs["placeholder"] = "e.g., 3 Simple Ways to Sleep Better"
            if name == "excerpt":
                w.attrs["placeholder"] = "Short teaser shown in cards and lists"
            if name == "body":
                w.attrs["placeholder"] = "Write the full tip/article here…"
            if name == "video_url":
                w.attrs["placeholder"] = "Paste a YouTube/Vimeo URL (e.g., https://youtu.be/...)"
            if name == "question":
                w.attrs["placeholder"] = "Ask a clear, concise question"

        # Helpful help_texts (UI hint beneath fields)
        if "excerpt" in self.fields:
            self.fields["excerpt"].help_text = "Short preview used on the homepage and listings."
        if "is_featured" in self.fields:
            self.fields["is_featured"].help_text = "Pin this content to the homepage ‘Latest Health Tips’."

# ---------- Content type forms ----------

class TextContentForm(TailwindFormMixin, forms.ModelForm):
    class Meta:
        model = Content
        fields = ["title", "excerpt", "body", "is_featured"]
        widgets = {
            "title": forms.TextInput(),
            "excerpt": forms.Textarea(attrs={"rows": 3}),
            "body": forms.Textarea(attrs={"rows": 12}),
        }

    def save(self, commit=True):
        obj = super().save(commit=False)
        obj.content_type = "text"
        if commit:
            obj.save()
        return obj

class ArticleContentForm(TailwindFormMixin, forms.ModelForm):
    class Meta:
        model = Content
        fields = ["title", "excerpt", "body", "image", "thumbnail", "is_featured"]
        widgets = {
            "title": forms.TextInput(),
            "excerpt": forms.Textarea(attrs={"rows": 3}),
            "body": forms.Textarea(attrs={"rows": 14}),
            "image": forms.ClearableFileInput(),
            "thumbnail": forms.ClearableFileInput(),
        }
        help_texts = {
            "image": "Hero image shown on cards and the article page.",
            "thumbnail": "Smaller image for lists (optional).",
        }

    def save(self, commit=True):
        obj = super().save(commit=False)
        obj.content_type = "article"
        if commit:
            obj.save()
        return obj

class VideoContentForm(TailwindFormMixin, forms.ModelForm):
    class Meta:
        model = Content
        fields = ["title", "excerpt", "video_url", "thumbnail", "is_featured"]
        widgets = {
            "title": forms.TextInput(),
            "excerpt": forms.Textarea(attrs={"rows": 3}),
            "video_url": forms.URLInput(),
            "thumbnail": forms.ClearableFileInput(),
        }
        help_texts = {
            "video_url": "YouTube or Vimeo link.",
            "thumbnail": "Optional cover image for the video post.",
        }

    def save(self, commit=True):
        obj = super().save(commit=False)
        obj.content_type = "video"
        if commit:
            obj.save()
        return obj

class PollContentForm(TailwindFormMixin, forms.ModelForm):
    class Meta:
        model = Content
        fields = ["title", "excerpt", "is_featured"]
        widgets = {
            "title": forms.TextInput(),
            "excerpt": forms.Textarea(attrs={"rows": 3}),
        }

    def save(self, commit=True):
        obj = super().save(commit=False)
        obj.content_type = "poll"
        obj.body = None
        obj.image = None
        obj.video_url = None
        if commit:
            obj.save()
        return obj

class PollForm(TailwindFormMixin, forms.ModelForm):
    class Meta:
        model = Poll
        fields = ["question"]
        widgets = {
            "question": forms.TextInput(),
        }

class PollOptionForm(TailwindFormMixin, forms.ModelForm):
    class Meta:
        model = PollOption
        fields = ["option_text"]
        widgets = {
            "option_text": forms.TextInput(attrs={"placeholder": "e.g., Yes, often"}),
        }

PollOptionFormSet = inlineformset_factory(
    Poll,
    PollOption,
    form=PollOptionForm,              # <-- styled options
    fields=["option_text"],
    extra=3,
    can_delete=True,
    min_num=2,
    validate_min=True,
    max_num=8,
)
