"""Auth views for the CMS dashboard (login / OTP verification / logout)."""
from django.contrib.auth import authenticate, login, logout, get_user_model
from django.shortcuts import render, redirect
from django.views import View
from django.contrib import messages

from .utils import send_otp_email

User = get_user_model()


class LoginView(View):
    template_name = "dashboard/auth/login.html"

    def get(self, request):
        if request.user.is_authenticated:
            return redirect("/cms/")
        return render(request, self.template_name)

    def post(self, request):
        identifier = request.POST.get("username", "").strip()
        password = request.POST.get("password", "")
        next_url = request.POST.get("next") or "/cms/"

        username = identifier
        if "@" in identifier:
            match = User.objects.filter(email__iexact=identifier).first()
            if match:
                username = match.username

        user = authenticate(request, username=username, password=password)
        if not user:
            messages.error(request, "Invalid username or password.")
            return render(request, self.template_name, {"username": identifier})

        if not user.email:
            messages.error(request, "This account has no email on file. Contact an administrator.")
            return render(request, self.template_name, {"username": identifier})

        code = user.generate_otp()
        if not send_otp_email(user, code):
            messages.error(request, "Could not send a verification email. Please try again shortly.")
            return render(request, self.template_name, {"username": identifier})

        request.session["pending_2fa_user_id"] = user.pk
        request.session["pending_2fa_next"] = next_url
        return redirect("cms_verify_otp")


class VerifyOTPView(View):
    template_name = "dashboard/auth/verify_otp.html"

    def _pending_user(self, request):
        user_id = request.session.get("pending_2fa_user_id")
        return User.objects.filter(pk=user_id).first() if user_id else None

    def get(self, request):
        user = self._pending_user(request)
        if not user:
            return redirect("cms_login")
        return render(request, self.template_name, {"email": user.email})

    def post(self, request):
        user = self._pending_user(request)
        if not user:
            return redirect("cms_login")

        code = request.POST.get("code", "").strip()
        if user.verify_otp(code):
            login(request, user)
            next_url = request.session.pop("pending_2fa_next", "/cms/")
            request.session.pop("pending_2fa_user_id", None)
            return redirect(next_url)

        user.refresh_from_db()
        if user.otp_attempts >= 5:
            user.clear_otp()
            request.session.pop("pending_2fa_user_id", None)
            request.session.pop("pending_2fa_next", None)
            messages.error(request, "Too many incorrect attempts. Please sign in again.")
            return redirect("cms_login")

        messages.error(request, "Incorrect or expired code. Please try again.")
        return render(request, self.template_name, {"email": user.email})


class ResendOTPView(View):
    def post(self, request):
        user_id = request.session.get("pending_2fa_user_id")
        user = User.objects.filter(pk=user_id).first() if user_id else None
        if not user:
            return redirect("cms_login")

        code = user.generate_otp()
        if send_otp_email(user, code):
            messages.success(request, "A new code has been sent to your email.")
        else:
            messages.error(request, "Could not send a verification email. Please try again shortly.")
        return redirect("cms_verify_otp")


class LogoutView(View):
    def get(self, request):
        logout(request)
        return redirect("/cms/auth/login/")
