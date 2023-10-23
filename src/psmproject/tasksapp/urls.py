from django.urls import path

from .views import (
    attachment,
    client,
    common,
    contractor,
    moderator_offers,
    moderator_tasks,
)

urlpatterns = [
    path("", client.TasksCurrentListView.as_view(), name="tasks-client-list"),
    path(
        "history/",
        client.TasksHistoricalListView.as_view(),
        name="tasks-client-history-list",
    ),
    path("moderator/", moderator_tasks.TasksListView.as_view(), name="tasks-moderator-list"),
    path("contractor/", contractor.TasksListView.as_view(), name="tasks-contractor-list"),
    path("moderator/new/", moderator_tasks.TasksNewListView.as_view(), name="tasks-moderator-list-new"),
    path("add/", client.TaskCreateView.as_view(), name="task-create"),
    path("<pk>/preview", common.TaskPreviewView.as_view(), name="task-preview"),
    path("<pk>/delete", common.TaskDeleteView.as_view(), name="task-delete"),
    path("<pk>/edit", client.TaskEditView.as_view(), name="task-edit"),
    path(
        "<pk>/moderator/edit",
        moderator_tasks.TaskEditView.as_view(),
        name="task-moderator-edit",
    ),
    path(
        "<pk>/moderator",
        moderator_tasks.TaskDetailView.as_view(),
        name="task-moderator-detail",
    ),
    path(
        "<pk>/contractor",
        contractor.TaskContractorDetailView.as_view(),
        name="task-contractor-detail",
    ),
    path(
        "<pk>/add_attachment",
        attachment.TaskAttachmentAddView.as_view(),
        name="task-add-attachment",
    ),
    path("<pk>", common.TaskDetailView.as_view(), name="task-detail"),
    path(
        "attachment/<pk>/delete",
        attachment.TaskAttachmentDeleteView.as_view(),
        name="task-attachment-delete",
    ),
    path("attachment/<pk>/download", attachment.download, name="task-attachment-download"),
    path("offers/", contractor.OfferListView.as_view(), name="offers-list"),
    path("offers/moderator/", moderator_offers.OfferListView.as_view(), name="offer-moderator-list"),
    path("offer/add/task/<task_pk>", contractor.OfferCreateView.as_view(), name="offer-create"),
    path("offer/task-search", contractor.TasksSearchView.as_view(), name="offer-task-search"),
    path("offer/moderator/<pk>", moderator_offers.OfferDetailView.as_view(), name="offer-moderator-detail"),
    path("offer/moderator/<pk>/edit", moderator_offers.OfferEditView.as_view(), name="offer-moderator-edit"),
    path("offer/<pk>", contractor.OfferDetailView.as_view(), name="offer-detail"),
    path("offer/<pk>/delete", contractor.OfferDeleteView.as_view(), name="offer-delete"),
    path("offer/<pk>/edit", contractor.OfferEditView.as_view(), name="offer-edit"),
    path("offers/client/", client.OfferClientListView.as_view(), name="offers-client-list"),
    path("<pk>/offers/", client.TaskOfferClientListView.as_view(), name="task-offers-list"),
    path("offers/client/<pk>", client.OfferClientAcceptView.as_view(), name="offer-client-accept"),
    path("solution/add/offer/<offer_pk>", contractor.SolutionCreateView.as_view(), name="solution-create"),
    path("solution/<pk>", contractor.SolutionDetailView.as_view(), name="solution-detail"),
    path("solution/<pk>/edit", contractor.SolutionEditView.as_view(), name="solution-edit"),
]
