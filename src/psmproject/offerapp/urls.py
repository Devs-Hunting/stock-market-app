from django.urls import path

from . import views

urlpatterns = [
    path("task-search", views.TasksSearchView.as_view(), name="offers-task-search"),
]
