# core/views_auth.py
from django.contrib.auth import login
from django.contrib.auth.views import LoginView as DjangoLoginView, LogoutView
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.views.generic import FormView

from .forms import EmailOrUsernameAuthenticationForm, TailwindUserCreationForm

class LoginView(DjangoLoginView):
    template_name = "registration/login.html"
    authentication_form = EmailOrUsernameAuthenticationForm
    redirect_authenticated_user = True

    def form_valid(self, form):
        # Handle "remember me"
        remember = form.cleaned_data.get("remember")
        if not remember:
            # Session expires when browser closes
            self.request.session.set_expiry(0)
        return super().form_valid(form)


class SignupView(FormView):
    template_name = "registration/signup.html"
    form_class = TailwindUserCreationForm
    success_url = reverse_lazy("blogger:dashboard")

    def form_valid(self, form):
        user = form.save()
        login(self.request, user)
        # respect ?next= if present
        nxt = self.request.GET.get("next") or self.request.POST.get("next")
        return redirect(nxt or self.get_success_url())
