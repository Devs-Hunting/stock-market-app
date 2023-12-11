from django.db.models import Q
from django.views.generic.base import TemplateView
from tasksapp.models import Offer, Task


class DashboardView(TemplateView):
    template_name = "dashboardapp/dashboard.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        my_active_tasks = Task.objects.filter(Q(client=self.request.user) & Q(status_lte=Task.TaskStatus.OBJECTIONS))

        my_active_jobs = Task.objects.filter(
            Q(selected_offer__isnull=False)
            & Q(status_lte=Task.TaskStatus.OBJECTIONS)
            & Q(selected_offer__contractor=self.request.user)
        )

        my_new_offers = Offer.objects.filter(Q(contractor=self.request.user) & Q(accepted=False))

        context["new_tasks"] = my_active_tasks.filter(status_lte=Task.TaskStatus.ON_HOLD).order_by("updated")[:5]
        context["tasks"] = my_active_tasks.filter(status=Task.TaskStatus.ON_GOING).order_by("updated")[:5]
        context["problematic_tasks"] = my_active_tasks.filter(status=Task.TaskStatus.OBJECTIONS).order_by("updated")[:5]

        context["jobs"] = my_active_jobs.filter(status=Task.TaskStatus.ON_GOING).order_by("updated")[:5]
        context["problematic_jobs"] = my_active_jobs.filter(status=Task.TaskStatus.OBJECTIONS).order_by("updated")[:5]

        context["new_offers"] = my_new_offers.order_by("updated")[:5]

        return context
