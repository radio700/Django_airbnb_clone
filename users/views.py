from django.views import View
from django.views.generic import FormView
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate,login,logout
from django.urls import reverse_lazy
from . import forms
# Create your views here.

class LoginView(View):
    def get(self, request):
        form = forms.LoginForm()
        return render(request, "users/login.html", {"form": form})
    
    def post(self, request):
        form = forms.LoginForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data.get("email")
            password = form.cleaned_data.get("password")
            user = authenticate(self.request, username=email, password=password)
            if user is not None:
                login(self.request, user)
                return redirect("core:home")
        return render(request, "users/login.html", {"form": form})

def log_out(request):
    logout(request)
    return redirect("core:home")

class SignupView(FormView):
    template_name = "users/signup.html"
    form_class = forms.SignupForm
    success_url = reverse_lazy("core:home")
    initial ={
        'first_name':'kim',
        'last_name':'sejung',
        'email':'radio700@hanmail.net',
    }

    def form_valid(self, form):
        form.save()
        email = form.cleaned_data.get("email")
        password = form.cleaned_data.get("password")
        user = authenticate(self.request, username=email, password=password)
        if user is not None:
            login(self.request, user)
        return super().form_valid(form)

