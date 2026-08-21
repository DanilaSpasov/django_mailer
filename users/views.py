from django.conf import settings
from django.contrib import messages
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import send_mail
from django.db import transaction
from django.shortcuts import redirect, render
from django.urls import reverse
from django.utils.encoding import force_bytes, force_str
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode

from users.forms import UserRegisterForm
from users.models import User


def register_view(request):
    if request.user.is_authenticated:
        return redirect("mailing:home")

    if request.method == "POST":
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            try:
                with transaction.atomic():
                    user = form.save(commit=False)
                    user.is_active = False
                    user.save()

                    uid = urlsafe_base64_encode(force_bytes(user.pk))
                    token = default_token_generator.make_token(user)
                    verification_url = request.build_absolute_uri(
                        reverse(
                            "users:verify_email",
                            kwargs={"uidb64": uid, "token": token},
                        )
                    )

                    send_mail(
                        subject="Подтверждение регистрации",
                        message=(
                            "Для подтверждения email перейдите по ссылке:\n"
                            f"{verification_url}"
                        ),
                        from_email=settings.DEFAULT_FROM_EMAIL,
                        recipient_list=[user.email],
                    )
            except Exception:
                form.add_error(
                    None,
                    "Не удалось отправить письмо. Попробуйте зарегистрироваться позже.",
                )
            else:
                messages.success(
                    request,
                    "Письмо с подтверждением отправлено на ваш email.",
                )
                return redirect("users:login")
    else:
        form = UserRegisterForm()

    return render(request, "users/register.html", {"form": form})


def verify_email(request, uidb64, token):
    try:
        user_id = force_str(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=user_id)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None

    if (
        user is not None
        and not user.is_active
        and default_token_generator.check_token(user, token)
    ):
        user.is_active = True
        user.save(update_fields=["is_active"])
        messages.success(request, "Email подтверждён. Теперь вы можете войти.")
    else:
        messages.error(request, "Ссылка подтверждения недействительна.")

    return redirect("users:login")
