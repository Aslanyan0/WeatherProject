from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from .forms import SignUpForm
from django.contrib import messages


def signup_view(request):
    if request.method == "POST":
        form = SignUpForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect("home")
    else:
        form = SignUpForm()
    return render(request, "accounts/signup.html", {"form": form})


def login_view(request):
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect("home")
        messages.error(request, "Invalid username or password")
        return redirect("accounts:login")
    return render(request, "accounts/login.html")


def logout_view(request):
    logout(request)
    return render(request, "accounts/logout.html")


from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.core.mail import send_mail
from django.contrib import messages
from .models import PasswordResetCode
from django.utils import timezone
from datetime import timedelta


def forgot_password(request):
    if request.method == "POST":
        email = request.POST.get("email")
        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            messages.error(request, "No account with this email.")
            return redirect("forgot_password")

        reset_code = PasswordResetCode.objects.create(user=user)
        reset_code.generate_code()

        send_mail(
            "Password Reset Code",
            f"Your password reset code is: {reset_code.code}",
            None,
            [email],
        )

        request.session["reset_user_id"] = user.id
        return redirect("verify_code")

    return render(request, "accounts/forgot_password.html")


def verify_code(request):
    if request.method == "POST":
        input_code = request.POST.get("code")
        user_id = request.session.get("reset_user_id")
        user = User.objects.get(id=user_id)
        code_obj = PasswordResetCode.objects.filter(user=user).last()

        if code_obj.code == input_code:
            return redirect("reset_password")
        else:
            messages.error(request, "Incorrect code.")
            return redirect("verify_code")

    return render(request, "accounts/verify_code.html")


def reset_password(request):
    if request.method == "POST":
        password = request.POST.get("password")
        repeat = request.POST.get("password2")

        if password != repeat:
            messages.error(request, "Passwords do not match.")
            return redirect("reset_password")

        user_id = request.session.get("reset_user_id")
        user = User.objects.get(id=user_id)
        user.set_password(password)
        user.save()

        messages.success(request, "Password changed successfully.")
        return redirect("login")

    return render(request, "accounts/reset_password.html")
