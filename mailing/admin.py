from django.contrib import admin

from mailing.models import Mailing, MailingAttempt, Message, Recipient


@admin.register(Recipient)
class RecipientAdmin(admin.ModelAdmin):
    list_display = ("id", "email", "full_name", "owner")
    list_display_links = ("email",)
    search_fields = ("email", "full_name")
    list_filter = ("owner",)


@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ("id", "subject")
    list_display_links = ("subject",)
    search_fields = ("subject", "body")


@admin.register(Mailing)
class MailingAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "start_time",
        "end_time",
        "status",
        "is_active",
        "message",
        "owner",
    )
    list_display_links = ("id",)
    search_fields = ("message__subject", "owner__email")
    list_filter = ("status", "is_active", "start_time", "end_time")
    filter_horizontal = ("recipients",)


@admin.register(MailingAttempt)
class MailingAttemptAdmin(admin.ModelAdmin):
    list_display = ("id", "mailing", "attempt_time", "status")
    list_display_links = ("id",)
    search_fields = ("mailing__message__subject", "server_response")
    list_filter = ("status", "attempt_time")
