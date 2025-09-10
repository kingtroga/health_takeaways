# core/forms.py
from django import forms
from django.contrib.auth import authenticate, get_user_model
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm

User = get_user_model()

INPUT = "block w-full rounded-lg border border-gray-300 px-3 py-2 text-gray-900 placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-health-primary/50 focus:border-health-primary"
CHECK = "h-4 w-4 rounded border-gray-300 text-health-primary focus:ring-health-primary"

class EmailOrUsernameAuthenticationForm(AuthenticationForm):
    """
    Login with either username OR email (field stays 'username' for Django's view).
    Adds a 'remember' checkbox.
    """
    remember = forms.BooleanField(required=False, widget=forms.CheckboxInput(attrs={"class": CHECK}))

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["username"].label = "Username or Email"
        self.fields["username"].widget.attrs.update({
            "placeholder": "Your username or email",
            "class": INPUT,
            "autocomplete": "username",
        })
        self.fields["password"].widget.attrs.update({
            "placeholder": "Your password",
            "class": INPUT,
            "autocomplete": "current-password",
        })

    def clean(self):
        """
        Accepts either username or email in the 'username' field.
        If an email is provided and matches exactly one user, authenticate with that username.
        """
        username = self.data.get(self.username_field) or self.data.get("username")
        password = self.data.get("password")

        # If user typed an email, try to resolve it to a username
        candidate = username
        if username and "@" in username:
            # case-insensitive email lookup
            try:
                user = User.objects.get(email__iexact=username)
                candidate = getattr(user, User.USERNAME_FIELD, "username")
            except User.DoesNotExist:
                # keep candidate as provided (will fail auth below)
                pass
            except User.MultipleObjectsReturned:
                # ambiguous email -> fall back to provided value
                pass

        # Let Django do the normal AuthenticationForm flow
        self.cleaned_data = {"username": candidate, "password": password}
        user = authenticate(self.request, username=candidate, password=password)
        if user is None:
            # re-run parent clean to raise the usual errors/messages
            return super().clean()
        self.confirm_login_allowed(user)
        self.user_cache = user
        return self.cleaned_data


class TailwindUserCreationForm(UserCreationForm):
    email = forms.EmailField(required=True)

    class Meta(UserCreationForm.Meta):
        model = User
        fields = ("username", "email")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["username"].widget.attrs.update({
            "placeholder": "Choose a username",
            "class": INPUT,
            "autocomplete": "username",
        })
        self.fields["email"].widget.attrs.update({
            "placeholder": "you@example.com",
            "class": INPUT,
            "autocomplete": "email",
        })
        self.fields["password1"].widget.attrs.update({
            "placeholder": "Create a strong password",
            "class": INPUT,
            "autocomplete": "new-password",
        })
        self.fields["password2"].widget.attrs.update({
            "placeholder": "Repeat password",
            "class": INPUT,
            "autocomplete": "new-password",
        })
