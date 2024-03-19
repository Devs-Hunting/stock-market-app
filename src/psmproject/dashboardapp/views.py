from typing import Any, List

from chatapp.models import Message
from django.conf import settings
from django.db.models import Q
from django.http import HttpRequest
from django.http.response import HttpResponse, HttpResponseRedirect
from django.urls import reverse
from django.views.generic.base import TemplateView
from tasksapp.models import Complaint, Offer, Solution, Task
from usersapp.helpers import SpecialUserMixin
from usersapp.models import BlockedUser


class DashboardView(TemplateView):
    """
    Class based view with dashboard for user. It shows task, offers, etc.
    It has dispatch method to redirect administrator, moderator and arbiter to their dashboard.
    """

    template_name = "dashboardapp/dashboard.html"

    def get_url_for_group(self):
        return {
            "Administrator": {
                "url": reverse("dashboard-admin"),
            },
            "Arbiter": {
                "url": reverse("dashboard-arbiter"),
            },
            "Moderator": {
                "url": reverse("dashboard-moderator"),
            },
        }

    def dispatch(self, request: HttpRequest, *args: Any, **kwargs: Any) -> HttpResponse:
        groups = [
            settings.GROUP_NAMES.get("ADMINISTRATOR"),
            settings.GROUP_NAMES.get("ARBITER"),
            settings.GROUP_NAMES.get("MODERATOR"),
        ]

        if self.request.user.groups.filter(name__in=groups).exists():
            user_group = self.request.user.groups.first().name
            url = self.get_url_for_group()[user_group]["url"]
            return HttpResponseRedirect(url)
        else:
            return super().dispatch(request, *args, **kwargs)

    def get_users_tasks(self):
        return Task.objects.filter(Q(client=self.request.user) & Q(status__lte=Task.TaskStatus.OBJECTIONS))

    def get_users_jobs(self):
        return Task.objects.filter(
            Q(selected_offer__isnull=False)
            & Q(status__lte=Task.TaskStatus.OBJECTIONS)
            & Q(selected_offer__contractor=self.request.user)
        )

    def get_user_offers(self):
        return Offer.objects.filter(Q(contractor=self.request.user) & Q(accepted=False))

    def get_new_offers(self):
        offers = self.get_user_offers()
        return offers.filter(task__selected_offer__isnull=True).order_by("-created")[:5]

    def get_lost_offers(self):
        offers = self.get_user_offers()
        return offers.filter(task__selected_offer__isnull=False).order_by("-task__updated")[:5]

    def get_new_messages(self):
        return (
            Message.objects.filter(chat__participants__user=self.request.user)
            .exclude(author=self.request.user)
            .order_by("-timestamp")[:5]
        )

    @staticmethod
    def last_tasks_filtered_by_status(tasks, statuses: List[int]):
        return tasks.filter(status__in=statuses).order_by("-updated")[:5]

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        if not self.request.user.is_authenticated:
            return context

        tasks = self.get_users_tasks()
        jobs = self.get_users_jobs()

        context.update(
            {
                "tasks": self.last_tasks_filtered_by_status(tasks, [Task.TaskStatus.ON_GOING]),
                "new_tasks": self.last_tasks_filtered_by_status(tasks, [Task.TaskStatus.OPEN, Task.TaskStatus.ON_HOLD]),
                "problematic_tasks": self.last_tasks_filtered_by_status(tasks, [Task.TaskStatus.OBJECTIONS]),
                "jobs": self.last_tasks_filtered_by_status(jobs, [Task.TaskStatus.ON_GOING]),
                "problematic_jobs": self.last_tasks_filtered_by_status(jobs, [Task.TaskStatus.OBJECTIONS]),
                "new_offers": self.get_new_offers(),
                "lost_offers": self.get_lost_offers(),
                "new_messages": self.get_new_messages(),
            }
        )

        return context


class DashboardModeratorView(SpecialUserMixin, TemplateView):
    """
    Class based view for Moderator dashboard. It shows new tasks, offers, solutions and new messages.
    """

    allowed_groups = [
        settings.GROUP_NAMES.get("MODERATOR"),
    ]
    template_name = "dashboardapp/dashboard_moderator.html"

    def get_new_tasks(self):
        return Task.objects.all()

    def get_new_solutions(self):
        return Solution.objects.all().order_by("-updated_at")[:10]

    def get_new_offers(self):
        return Offer.objects.filter(Q(accepted=False)).order_by("-created")[:10]

    def get_new_messages(self):
        return Message.objects.all()[:10]

    def get_moderator_messages(self):
        return (
            Message.objects.filter(chat__participants__user=self.request.user)
            .exclude(author=self.request.user)
            .order_by("-timestamp")[:5]
        )

    @staticmethod
    def last_tasks_filtered_by_status(tasks, statuses: List[int]):
        return tasks.filter(status__in=statuses).order_by("-updated")[:10]

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        if not self.request.user.is_authenticated:
            return context

        tasks = self.get_new_tasks()

        context.update(
            {
                "tasks": self.last_tasks_filtered_by_status(tasks, [Task.TaskStatus.ON_GOING]),
                "new_tasks": self.last_tasks_filtered_by_status(tasks, [Task.TaskStatus.OPEN, Task.TaskStatus.ON_HOLD]),
                "problematic_tasks": self.last_tasks_filtered_by_status(tasks, [Task.TaskStatus.OBJECTIONS]),
                "new_offers": self.get_new_offers(),
                "new_solutions": self.get_new_solutions(),
                "new_messages": self.get_new_messages(),
                "moderator_messages": self.get_moderator_messages(),
            }
        )

        return context


class DashboardArbiterView(SpecialUserMixin, TemplateView):
    """
    Class based view for Arbiter dashboard. It shows new complaints, complaints taken by Arbiter and new messages.
    """

    allowed_groups = [
        settings.GROUP_NAMES.get("ARBITER"),
    ]
    template_name = "dashboardapp/dashboard_arbiter.html"

    def get_arbiter_messages(self):
        return (
            Message.objects.filter(chat__participants__user=self.request.user)
            .exclude(author=self.request.user)
            .order_by("-timestamp")[:10]
        )

    def get_new_complaints(self):
        return Complaint.objects.filter(Q(arbiter=None)).order_by("-created_at")[:10]

    def get_active_complaints(self):
        return Complaint.objects.filter(Q(arbiter=self.request.user)).order_by("-created_at")[:10]

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        if not self.request.user.is_authenticated:
            return context

        context.update(
            {
                "new_complaints": self.get_new_complaints(),
                "active_complaints": self.get_active_complaints(),
                "arbiter_messages": self.get_arbiter_messages(),
            }
        )

        return context


class DashboardAdminView(SpecialUserMixin, TemplateView):
    """
    Class based View for Administrator Dashboard. It contains messages, blocked users, complaints, new tasks and offers.
    """

    allowed_groups = [
        settings.GROUP_NAMES.get("ADMINISTRATOR"),
    ]

    template_name = "dashboardapp/dashboard_admin.html"

    def get_new_messages(self):
        return Message.objects.all()[:10]

    def get_blocked_users(self):
        return BlockedUser.objects.all().order_by("-blocking_start_date")[:10]

    def get_new_complaints(self):
        return Complaint.objects.filter(Q(arbiter=None)).order_by("-created_at")[:10]

    def get_active_complaints(self):
        return Complaint.objects.filter(Q(closed=False)).order_by("-created_at")[:10]

    def get_tasks(self):
        return Task.objects.all()

    def get_new_offers(self):
        return Offer.objects.filter(Q(accepted=False)).order_by("-created")[:10]

    @staticmethod
    def last_tasks_filtered_by_status(tasks, statuses: List[int]):
        return tasks.filter(status__in=statuses).order_by("-updated")[:10]

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        if not self.request.user.is_authenticated:
            return context

        tasks = self.get_tasks()

        context.update(
            {
                "blocked_users": self.get_blocked_users(),
                "new_complaints": self.get_new_complaints(),
                "active_complaints": self.get_active_complaints(),
                "new_messages": self.get_new_messages(),
                "tasks": self.last_tasks_filtered_by_status(tasks, [Task.TaskStatus.ON_GOING]),
                "new_tasks": self.last_tasks_filtered_by_status(tasks, [Task.TaskStatus.OPEN, Task.TaskStatus.ON_HOLD]),
                "problematic_tasks": self.last_tasks_filtered_by_status(tasks, [Task.TaskStatus.OBJECTIONS]),
                "new_offers": self.get_new_offers(),
            }
        )

        return context
