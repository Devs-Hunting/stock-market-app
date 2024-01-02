from typing import List

from chatapp.models import Message
from django.db.models import Q
from django.views.generic.base import TemplateView
from tasksapp.models import Offer, Task


class DashboardView(TemplateView):
    template_name = "dashboardapp/dashboard.html"

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
