from django.urls import path
from tasksapp import attachment_views, views

urlpatterns = [
    path("", views.ClientTasksListView.as_view(), name="tasks-client-list"),
    path("all", views.StaffTasksListView.as_view(), name="tasks-all-list"),
    path("<pk>/", views.TaskDetailView.as_view(), name="task-detail"),
    path("add", views.TaskCreateView.as_view(), name="task-create"),
    path("<pk>/delete", views.TaskDeleteView.as_view(), name="task-delete"),
    path("<pk>/edit", views.TaskEditView.as_view(), name="task-edit"),
    path(
        "<pk>/add_attachment",
        attachment_views.TaskAttachmentAddView.as_view(),
        name="task-add-attachment",
    ),
    path(
        "attachment/<pk>/delete",
        attachment_views.TaskAttachmentDeleteView.as_view(),
        name="task-delete-attachment",
    ),
]
