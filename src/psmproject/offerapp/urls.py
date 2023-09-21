from django.urls import path

from .views import contractor, moderator

urlpatterns = [
    path("", contractor.OfferListView.as_view(), name="offers-list"),
    path("add/task/<task_pk>", contractor.OfferCreateView.as_view(), name="offer-create"),
    path("task-search", contractor.TasksSearchView.as_view(), name="offer-task-search"),
    path("moderator/", moderator.OfferListView.as_view(), name="offer-moderator-list"),
    path("<pk>", contractor.OfferDetailView.as_view(), name="offer-detail"),
    path("<pk>/delete", contractor.OfferDeleteView.as_view(), name="offer-delete"),
    path("<pk>/edit", contractor.OfferEditView.as_view(), name="offer-edit"),
]
