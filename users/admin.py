from django.contrib import admin

from users.models import User


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "email",
        "first_name",
        "last_name",
        "is_staff",
        "is_active",
        "is_email_verified",
        "is_blocked",
    )
    list_filter = ("is_staff", "is_active", "is_email_verified", "is_blocked")
    search_fields = ("email", "first_name", "last_name")
