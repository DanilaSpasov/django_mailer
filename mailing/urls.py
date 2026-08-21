from django.urls import path

from mailing.views import (
    RecipientCreateView,
    RecipientDeleteView,
    RecipientDetailView,
    RecipientListView,
    RecipientUpdateView,
)


app_name = "mailing"

urlpatterns = [
    path("recipients/", RecipientListView.as_view(), name="recipient_list"),
    path(
        "recipients/create/",
        RecipientCreateView.as_view(),
        name="recipient_create",
    ),
    path(
        "recipients/<int:pk>/",
        RecipientDetailView.as_view(),
        name="recipient_detail",
    ),
    path(
        "recipients/<int:pk>/edit/",
        RecipientUpdateView.as_view(),
        name="recipient_update",
    ),
    path(
        "recipients/<int:pk>/delete/",
        RecipientDeleteView.as_view(),
        name="recipient_delete",
    ),
]
