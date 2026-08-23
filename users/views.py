from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required, permission_required
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import send_mail
from django.db import transaction
from django.http import Http404
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.utils.encoding import force_bytes, force_str
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode
from django.views.decorators.http import require_POST
from django.views.generic import ListView

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
                    user.is_email_verified = False
                    user.is_blocked = False
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
        and not user.is_email_verified
        and default_token_generator.check_token(user, token)
    ):
        user.is_email_verified = True
        user.is_active = not user.is_blocked
        user.save(update_fields=["is_email_verified", "is_active"])
        if user.is_blocked:
            messages.warning(request, "Email подтверждён, но аккаунт заблокирован.")
        else:
            messages.success(request, "Email подтверждён. Теперь вы можете войти.")
    else:
        messages.error(request, "Ссылка подтверждения недействительна.")

    return redirect("users:login")


class UserListView(LoginRequiredMixin, PermissionRequiredMixin, ListView):
    model = User
    template_name = "users/user_list.html"
    context_object_name = "user_list"
    permission_required = "users.can_view_users"
    raise_exception = True

    def get_queryset(self):
        return super().get_queryset().order_by("email")


@login_required
@permission_required("users.can_block_users", raise_exception=True)
@require_POST
def set_user_block(request, pk, action):
    if action not in {"block", "unblock"}:
        raise Http404

    selected_user = get_object_or_404(User, pk=pk)

    if selected_user == request.user:
        messages.error(request, "Нельзя заблокировать собственный аккаунт.")
    elif selected_user.is_superuser:
        messages.error(request, "Нельзя заблокировать суперпользователя.")
    else:
        selected_user.is_blocked = action == "block"
        selected_user.is_active = (
            selected_user.is_email_verified and not selected_user.is_blocked
        )
        selected_user.save(update_fields=["is_blocked", "is_active"])

        if selected_user.is_blocked:
            messages.success(request, "Пользователь заблокирован.")
        else:
            messages.success(request, "Пользователь разблокирован.")

    return redirect("users:user_list")
