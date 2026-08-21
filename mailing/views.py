from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import PermissionDenied
from django.urls import reverse, reverse_lazy
from django.views.generic import (
    CreateView,
    DeleteView,
    DetailView,
    ListView,
    UpdateView,
)

from mailing.forms import RecipientForm
from mailing.models import Recipient


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
