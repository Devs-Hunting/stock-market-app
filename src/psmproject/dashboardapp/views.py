from chatapp.models import Message
from django.db.models import Q
from django.views.generic.base import TemplateView
from tasksapp.models import Offer, Task


class DashboardView(TemplateView):
    template_name = "dashboardapp/dashboard.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        if not self.request.user.is_authenticated:
            return context

        my_active_tasks = Task.objects.filter(Q(client=self.request.user) & Q(status__lte=Task.TaskStatus.OBJECTIONS))

        my_active_jobs = Task.objects.filter(
            Q(selected_offer__isnull=False)
            & Q(status__lte=Task.TaskStatus.OBJECTIONS)
            & Q(selected_offer__contractor=self.request.user)
        )

        my_offers = Offer.objects.filter(Q(contractor=self.request.user) & Q(accepted=False))
        context["tasks"] = my_active_tasks.filter(status=Task.TaskStatus.ON_GOING).order_by("-updated")[:5]
        context["new_tasks"] = my_active_tasks.filter(status__lte=Task.TaskStatus.ON_HOLD).order_by("-updated")[:5]
        context["problematic_tasks"] = my_active_tasks.filter(status=Task.TaskStatus.OBJECTIONS).order_by("-updated")[
            :5
        ]

        context["jobs"] = my_active_jobs.filter(status=Task.TaskStatus.ON_GOING).order_by("-updated")[:5]
        context["problematic_jobs"] = my_active_jobs.filter(status=Task.TaskStatus.OBJECTIONS).order_by("-updated")[:5]

        context["new_offers"] = my_offers.filter(task__selected_offer__isnull=True).order_by("-created")[:5]
        context["lost_offers"] = my_offers.filter(task__selected_offer__isnull=False).order_by("-task__updated")[:5]

        context["new_messages"] = (
            Message.objects.filter(chat__participants__user=self.request.user)
            .exclude(author=self.request.user)
            .order_by("-timestamp")[:5]
        )

        return context
