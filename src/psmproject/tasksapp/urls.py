from django.urls import path

from .views import attachment, client, common, moderator

urlpatterns = [
    path("", client.TasksCurrentListView.as_view(), name="tasks-client-list"),
    path(
        "history/",
        client.TasksHistoricalListView.as_view(),
        name="tasks-client-history-list",
    ),
    path("moderator/", moderator.TasksListView.as_view(), name="tasks-moderator-list"),
    path("add/", client.TaskCreateView.as_view(), name="task-create"),
    path("<pk>", common.TaskDetailView.as_view(), name="task-detail"),
    path("<pk>/delete", common.TaskDeleteView.as_view(), name="task-delete"),
    path("<pk>/edit", client.TaskEditView.as_view(), name="task-edit"),
    path(
        "<pk>/moderator/edit",
        moderator.TaskEditView.as_view(),
        name="task-moderator-edit",
    ),
    path(
        "<pk>/add_attachment",
        attachment.TaskAttachmentAddView.as_view(),
        name="task-add-attachment",
    ),
    path(
        "attachment/<pk>/delete",
        attachment.TaskAttachmentDeleteView.as_view(),
        name="task-attachment-delete",
    ),
    path("attachment/<pk>/download", attachment.download, name="task-attachment-download"),
]
