from django.urls import path

from . import views

urlpatterns = [
    path("", views.OfferListView.as_view(), name="offers-list"),
    path("add/task/<task_pk>", views.OfferCreateView.as_view(), name="offer-create"),
    path("task-search", views.TasksSearchView.as_view(), name="offer-task-search"),
]
