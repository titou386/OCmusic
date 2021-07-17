from django.urls import reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import LoginView
from django.views.generic import CreateView, ListView
from django.shortcuts import redirect
from .forms import RegisterForm, LoginForm

from items.models import Item


class IndexView(LoginRequiredMixin, ListView):
    template_name = "account/index.html"
    context_object_name = "items"
    model = Item

    def get_queryset(self):
        return super().get_queryset().filter(like=self.request.user)


class SignInView(LoginView):
    template_name = "account/auth.html"
    form_class = LoginForm
    success_url = reverse_lazy("account")

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect(reverse_lazy("account"))
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
            return redirect(reverse_lazy("account"))
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["action"] = "register"
        return context
