from django.contrib import messages
from django.contrib.auth import login
from django.shortcuts import redirect, render

from users.forms import UserRegisterForm


def register_view(request):
    if request.user.is_authenticated:
        return redirect("mailing:home")

    if request.method == "POST":
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, "Регистрация успешно завершена.")
            return redirect("mailing:home")
    else:
        form = UserRegisterForm()

    return render(request, "users/register.html", {"form": form})
