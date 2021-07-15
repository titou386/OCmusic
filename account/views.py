from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import TemplateView
from django.contrib.auth.views import LoginView
from django.views.generic import CreateView
from django.shortcuts import redirect
from .forms import RegisterForm, LoginForm


class IndexView(LoginRequiredMixin, TemplateView):
    template_name = "account/index.html"


class SignInView(LoginView):
    template_name = "account/auth.html"
    form_class = LoginForm
    success_url = "/account/"

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect("account")
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["action"] = "login"
        return context


class SignUpView(CreateView):
    template_name = "account/auth.html"
    form_class = RegisterForm
    success_url = "/account/"

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect("account")
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["action"] = "register"
        return context
