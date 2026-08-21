from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import PermissionDenied
from django.core.mail import send_mail
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse, reverse_lazy
from django.utils import timezone
from django.views.decorators.http import require_POST
from django.views.generic import (
    CreateView,
    DeleteView,
    DetailView,
    ListView,
    UpdateView,
)

from mailing.forms import MailingForm, MessageForm, RecipientForm
from mailing.models import Mailing, MailingAttempt, Message, Recipient


@login_required
def home_view(request):
    current_time = timezone.now()
    user_mailings = Mailing.objects.filter(owner=request.user)

    for mailing in user_mailings:
        mailing.update_status()

    user_attempts = MailingAttempt.objects.filter(
        mailing__owner=request.user,
    )
    successful_attempts = user_attempts.filter(
        status=MailingAttempt.STATUS_SUCCESS,
    ).count()
    failed_attempts = user_attempts.filter(
        status=MailingAttempt.STATUS_FAILED,
    ).count()

    context = {
        "total_mailings": user_mailings.count(),
        "active_mailings": user_mailings.filter(
            start_time__lte=current_time,
            end_time__gte=current_time,
            status=Mailing.STATUS_STARTED,
        ).count(),
        "unique_recipients": Recipient.objects.filter(owner=request.user).count(),
        "successful_attempts": successful_attempts,
        "failed_attempts": failed_attempts,
        "sent_messages": successful_attempts,
    }
    return render(request, "mailing/home.html", context)


class RecipientListView(LoginRequiredMixin, ListView):
    model = Recipient
    template_name = "mailing/recipient_list.html"
    context_object_name = "recipients"

    def get_queryset(self):
        return super().get_queryset().filter(owner=self.request.user)


class RecipientCreateView(LoginRequiredMixin, CreateView):
    model = Recipient
    form_class = RecipientForm
    template_name = "mailing/recipient_form.html"
    success_url = reverse_lazy("mailing:recipient_list")

    def form_valid(self, form):
        form.instance.owner = self.request.user
        return super().form_valid(form)


class RecipientDetailView(LoginRequiredMixin, DetailView):
    model = Recipient
    template_name = "mailing/recipient_detail.html"
    context_object_name = "recipient"

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return self.handle_no_permission()

        recipient = self.get_object()
        if recipient.owner != request.user:
            raise PermissionDenied

        return super().dispatch(request, *args, **kwargs)


class RecipientUpdateView(LoginRequiredMixin, UpdateView):
    model = Recipient
    form_class = RecipientForm
    template_name = "mailing/recipient_form.html"

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return self.handle_no_permission()

        recipient = self.get_object()
        if recipient.owner != request.user:
            raise PermissionDenied

        return super().dispatch(request, *args, **kwargs)

    def get_success_url(self):
        return reverse("mailing:recipient_detail", kwargs={"pk": self.object.pk})


class RecipientDeleteView(LoginRequiredMixin, DeleteView):
    model = Recipient
    template_name = "mailing/recipient_confirm_delete.html"
    context_object_name = "recipient"
    success_url = reverse_lazy("mailing:recipient_list")

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return self.handle_no_permission()

        recipient = self.get_object()
        if recipient.owner != request.user:
            raise PermissionDenied

        return super().dispatch(request, *args, **kwargs)


class MessageListView(LoginRequiredMixin, ListView):
    model = Message
    template_name = "mailing/message_list.html"
    context_object_name = "message_list"


class MessageCreateView(LoginRequiredMixin, CreateView):
    model = Message
    form_class = MessageForm
    template_name = "mailing/message_form.html"
    success_url = reverse_lazy("mailing:message_list")


class MessageDetailView(LoginRequiredMixin, DetailView):
    model = Message
    template_name = "mailing/message_detail.html"
    context_object_name = "message"


class MessageUpdateView(LoginRequiredMixin, UpdateView):
    model = Message
    form_class = MessageForm
    template_name = "mailing/message_form.html"

    def get_success_url(self):
        return reverse("mailing:message_detail", kwargs={"pk": self.object.pk})


class MessageDeleteView(LoginRequiredMixin, DeleteView):
    model = Message
    template_name = "mailing/message_confirm_delete.html"
    context_object_name = "message"
    success_url = reverse_lazy("mailing:message_list")


class MailingListView(LoginRequiredMixin, ListView):
    model = Mailing
    template_name = "mailing/mailing_list.html"
    context_object_name = "mailings"

    def get_queryset(self):
        return super().get_queryset().filter(owner=self.request.user)


class MailingCreateView(LoginRequiredMixin, CreateView):
    model = Mailing
    form_class = MailingForm
    template_name = "mailing/mailing_form.html"
    success_url = reverse_lazy("mailing:mailing_list")

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["user"] = self.request.user
        return kwargs

    def form_valid(self, form):
        form.instance.owner = self.request.user
        return super().form_valid(form)


class MailingDetailView(LoginRequiredMixin, DetailView):
    model = Mailing
    template_name = "mailing/mailing_detail.html"
    context_object_name = "mailing"

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return self.handle_no_permission()

        mailing = super().get_object()
        if mailing.owner != request.user:
            raise PermissionDenied

        return super().dispatch(request, *args, **kwargs)

    def get_object(self, queryset=None):
        mailing = super().get_object(queryset)
        mailing.update_status()
        return mailing


class MailingUpdateView(LoginRequiredMixin, UpdateView):
    model = Mailing
    form_class = MailingForm
    template_name = "mailing/mailing_form.html"

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return self.handle_no_permission()

        mailing = self.get_object()
        if mailing.owner != request.user:
            raise PermissionDenied

        return super().dispatch(request, *args, **kwargs)

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["user"] = self.request.user
        return kwargs

    def get_success_url(self):
        return reverse("mailing:mailing_detail", kwargs={"pk": self.object.pk})


class MailingDeleteView(LoginRequiredMixin, DeleteView):
    model = Mailing
    template_name = "mailing/mailing_confirm_delete.html"
    context_object_name = "mailing"
    success_url = reverse_lazy("mailing:mailing_list")

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return self.handle_no_permission()

        mailing = self.get_object()
        if mailing.owner != request.user:
            raise PermissionDenied

        return super().dispatch(request, *args, **kwargs)


@login_required
@require_POST
def send_mailing_view(request, pk):
    mailing = get_object_or_404(
        Mailing,
        pk=pk,
        owner=request.user,
    )
    current_time = timezone.now()

    if not mailing.start_time <= current_time <= mailing.end_time:
        messages.error(
            request,
            "Рассылку можно запустить только в установленный период.",
        )
        return redirect("mailing:mailing_detail", pk=mailing.pk)

    successful_attempts = 0
    failed_attempts = 0

    for recipient in mailing.recipients.all():
        try:
            sent_count = send_mail(
                subject=mailing.message.subject,
                message=mailing.message.body,
                from_email=None,
                recipient_list=[recipient.email],
            )

            if sent_count:
                MailingAttempt.objects.create(
                    mailing=mailing,
                    status=MailingAttempt.STATUS_SUCCESS,
                    server_response=f"Письмо отправлено: {recipient.email}",
                )
                successful_attempts += 1
            else:
                MailingAttempt.objects.create(
                    mailing=mailing,
                    status=MailingAttempt.STATUS_FAILED,
                    server_response=f"Письмо не отправлено: {recipient.email}",
                )
                failed_attempts += 1

        except Exception as error:
            MailingAttempt.objects.create(
                mailing=mailing,
                status=MailingAttempt.STATUS_FAILED,
                server_response=f"{recipient.email}: {error}",
            )
            failed_attempts += 1

    add_message = (
        messages.warning
        if failed_attempts or not successful_attempts
        else messages.success
    )
    add_message(
        request,
        (
            f"Рассылка завершена. Успешно: {successful_attempts}, "
            f"неуспешно: {failed_attempts}."
        ),
    )
    return redirect("mailing:mailing_detail", pk=mailing.pk)
