"""Auth views for the CMS dashboard (login / logout / profile)."""
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.views import View
from django.contrib import messages


class LoginView(View):
    template_name = "dashboard/auth/login.html"

    def get(self, request):
        if request.user.is_authenticated:
            return redirect("/cms/")
        return render(request, self.template_name)

    def post(self, request):
        username = request.POST.get("username", "").strip()
        password = request.POST.get("password", "")
        user = authenticate(request, username=username, password=password)
        if user:
            login(request, user)
            return redirect(request.POST.get("next", "/cms/"))
        messages.error(request, "Invalid username or password.")
        return render(request, self.template_name, {"username": username})


class LogoutView(View):
    def get(self, request):
        logout(request)
        return redirect("/cms/auth/login/")
