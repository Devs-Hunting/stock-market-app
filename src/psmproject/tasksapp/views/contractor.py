from django.conf import settings
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.db.models import Q
from django.forms.models import model_to_dict
from django.http import HttpResponseRedirect
from django.urls import reverse, reverse_lazy
from django.views.generic.detail import DetailView
from django.views.generic.edit import CreateView, DeleteView, UpdateView
from django.views.generic.list import ListView
from usersapp.helpers import skills_from_text
from usersapp.models import Skill

from ..forms.offers import OfferForm, TaskSearchForm
from ..forms.solution import SolutionAttachmentForm, SolutionForm
from ..models import Offer, Solution, SolutionAttachment, Task
from .common import TaskDetailView

SKILL_PREFIX = "query-skill-"


class TasksSearchView(LoginRequiredMixin, ListView):
    """
    This is a search task list view for contractor to find new to tasks for an offer. \
    Tasks can be filtered by URL parameter "q". Search phrase will be compared against task title or task
    description. Tasks can also be filtered by skills, budget end end-date. Result list is limited/paginated.
    """

    model = Task
    template_name = "tasksapp/task_search.html"
    paginate_by = 10
    search_phrase_min = 3

    def get_queryset(self, **kwargs):
        queryset = Task.objects.filter(status=Task.TaskStatus.OPEN).exclude(
            Q(client=self.request.user) | Q(offers__contractor=self.request.user)
        )
        form = kwargs.get("form")
        if not form or not form.is_valid():
            return queryset.order_by("-id")

        phrase = form.cleaned_data.get("query", "")
        budget = form.cleaned_data.get("budget")
        min_days_to_complete = form.cleaned_data.get("min_days_to_complete")
        max_days_to_complete = form.cleaned_data.get("max_days_to_complete")
        selected_skills = kwargs.get("selected_skills")

        if len(phrase) >= TasksSearchView.search_phrase_min:
            queryset = queryset.filter(Q(title__contains=phrase) | Q(description__contains=phrase))
        if budget:
            queryset = queryset.filter(budget__gte=budget).distinct()
        if min_days_to_complete:
            queryset = queryset.filter(days_to_complete__gte=min_days_to_complete).distinct()
        if max_days_to_complete:
            queryset = queryset.filter(days_to_complete__lte=max_days_to_complete).distinct()
        if selected_skills:
            for skill in selected_skills:
                queryset = queryset.filter(skills=skill).distinct()
        return queryset.order_by("-id")

    def get_context_data(self, **kwargs):
        """Add skills list for skill selection to context,
        as well as skill prefix which is used to generate skill field names in form"""
        context = super().get_context_data(**kwargs)
        skills = Skill.objects.all()

        selected_skills = kwargs.get("selected_skills")
        if selected_skills:
            context["selected_skills"] = selected_skills
            selected_ids = [skill.id for skill in selected_skills]
            skills = skills.exclude(id__in=selected_ids)
        form = kwargs.get("form")
        if form:
            context["form"] = kwargs.get("form")
            context["filtered"] = True
        else:
            context["form"] = TaskSearchForm()

        context["skills"] = [model_to_dict(skill) for skill in list(skills)]
        context["skill_id_prefix"] = SKILL_PREFIX
        return context

    def get(self, request, *args, **kwargs):
        form = TaskSearchForm(request.GET) if bool(request.GET) else None
        selected_skills = [item[1] for item in self.request.GET.items() if item[0].startswith(SKILL_PREFIX)]
        skills_objects = skills_from_text(selected_skills)
        self.object_list = self.get_queryset(form=form, selected_skills=skills_objects)
        return self.render_to_response(self.get_context_data(form=form, selected_skills=skills_objects))


class OfferListView(LoginRequiredMixin, ListView):
    """
    This is a base view class for displaying list of offers created by currently logged-in user (contractor), ordered
    from newest. Offers can be filtered by URL parameter "q". Search phrase will be compared against offer description,
    task name or task description. Result list is limited/paginated
    """

    model = Offer
    template_name_suffix = "s_list"
    paginate_by = 10
    search_phrase_min = 3

    def get_queryset(self):
        phrase = self.request.GET.get("q", "")
        queryset = Offer.objects.filter(contractor=self.request.user).order_by("-id")
        if len(phrase) >= OfferListView.search_phrase_min:
            queryset = queryset.filter(
                Q(description__contains=phrase)
                | Q(task__title__contains=phrase)
                | Q(task__description__contains=phrase)
            )
        return queryset


class TasksListView(LoginRequiredMixin, ListView):
    """
    This View displays list of tasks which contractor is currently assigned-to, ordered from newest. Tasks can be
    filtered by URL parameter "q". Search phrase will be compared against task title or task description.
    Result list is limited/paginated
    """

    model = Task
    template_name_suffix = "s_list_contractor"
    paginate_by = 10
    search_phrase_min = 3

    def get_queryset(self):
        queryset = Task.objects.filter(
            Q(selected_offer__isnull=False)
            & Q(status=Task.TaskStatus.ON_GOING)
            & Q(selected_offer__contractor=self.request.user)
        ).order_by("-id")

        phrase = self.request.GET.get("q", "")
        if len(phrase) >= TasksListView.search_phrase_min:
            queryset = queryset.filter(Q(title__contains=phrase) | Q(description__contains=phrase))
        return queryset


class TasksClosedListView(LoginRequiredMixin, ListView):
    """
    This View displays list of closed tasks which contractor was assigned-to, ordered from newest. Tasks can be
    filtered by URL parameter "q". Search phrase will be compared against task title or task description.
    Result list is limited/paginated
    """

    model = Task
    template_name_suffix = "s_list_contractor"
    paginate_by = 10
    search_phrase_min = 3

    def get_queryset(self):
        queryset = Task.objects.filter(
            Q(selected_offer__isnull=False)
            & Q(status=Task.TaskStatus.COMPLETED)
            & Q(selected_offer__contractor=self.request.user)
        ).order_by("-id")

        phrase = self.request.GET.get("q", "")
        if len(phrase) >= TasksListView.search_phrase_min:
            queryset = queryset.filter(Q(title__contains=phrase) | Q(description__contains=phrase))
        return queryset


class TaskContractorDetailView(TaskDetailView):
    """
    This View displays task details and all attachments, without possibility to edit anything. Version for contractor
    """

    template_name_suffix = "_detail_contractor"


class OfferCreateView(LoginRequiredMixin, CreateView):
    """
    This View creates new offers with logged-in user as a contractor and task passed as an url parameter "task"
    """

    model = Offer
    form_class = OfferForm
    success_url = reverse_lazy("offers-list")

    def dispatch(self, request, *args, **kwargs):
        task_id = kwargs.get("task_pk")
        self.task = Task.objects.filter(id=task_id).first()
        if not self.task:
            messages.warning(self.request, "task not found")
            return HttpResponseRedirect(OfferCreateView.success_url)
        if not self.task.status == Task.TaskStatus.OPEN:
            messages.warning(self.request, "task does not accept new offers")
            return HttpResponseRedirect(OfferCreateView.success_url)
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["task"] = self.task
        return context

    def form_valid(self, form):
        """Assign current user and task to the new offer"""

        form.instance.contractor = self.request.user
        form.instance.task = self.task
        return super().form_valid(form)


class OfferEditView(UserPassesTestMixin, UpdateView):
    """
    This View allows to edit existing offer. This is the version of the view for the contractor
    """

    model = Offer
    form_class = OfferForm

    def get_success_url(self):
        offer = self.get_object()
        return reverse("offer-detail", kwargs={"pk": offer.id})

    def test_func(self):
        offer = self.get_object()
        user = self.request.user
        return user == offer.contractor

    def handle_no_permission(self):
        if not self.request.user.is_authenticated:
            return super().handle_no_permission()
        return HttpResponseRedirect(self.get_success_url())


class OfferDetailView(LoginRequiredMixin, DetailView):
    """
    This View displays offer details without possibility to edit anything
    """

    model = Offer

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["is_contractor"] = self.request.user == self.object.contractor
        context["is_client"] = self.request.user == self.object.task.client
        return context


class OfferDeleteView(UserPassesTestMixin, DeleteView):
    """
    This view is used delete Offer. Only offer contractor or moderator can do this. Offer can only be deleted before it
    is accepted
    """

    model = Offer
    allowed_groups = [
        settings.GROUP_NAMES.get("MODERATOR"),
    ]
    template_name = "tasksapp/offer_confirm_delete.html"

    def get_success_url(self):
        return reverse_lazy("offers-list")

    def test_func(self):
        offer = self.get_object()
        if offer.accepted:
            messages.warning(self.request, "cannot delete accepted offer")
            return False
        user = self.request.user
        in_allowed_group = user.groups.filter(name__in=OfferDeleteView.allowed_groups).exists()
        return user == offer.contractor or in_allowed_group

    def handle_no_permission(self):
        if not self.request.user.is_authenticated:
            return super().handle_no_permission()
        redirect_url = self.get_success_url()
        return HttpResponseRedirect(redirect_url)


class SolutionCreateView(UserPassesTestMixin, CreateView):
    """
    This View creates new offers with logged-in user as a contractor and task passed as an url parameter "task"
    """

    model = Solution
    form_class = SolutionForm
    attachment_form_class = SolutionAttachmentForm
    prefix_form = "attachment_form"
    template_name = "tasksapp/solution_form.html"
    redirect_url = reverse_lazy("tasks-contractor-list")

    def test_func(self):
        return self.request.user == self.offer.contractor

    def handle_no_permission(self):
        if not self.request.user.is_authenticated:
            return super().handle_no_permission()
        return HttpResponseRedirect(SolutionCreateView.redirect_url)

    def get_success_url(self):
        return reverse("task-contractor-detail", kwargs={"pk": self.offer.task.id})

    def dispatch(self, request, *args, **kwargs):
        offer_id = kwargs.get("offer_pk")
        self.offer = Offer.objects.filter(id=offer_id).first()
        if not self.offer:
            messages.warning(self.request, "offer not found")
            return HttpResponseRedirect(SolutionCreateView.redirect_url)
        if self.offer.solution:
            messages.warning(self.request, "offer already has solution")
            return HttpResponseRedirect(SolutionCreateView.redirect_url)
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["task"] = self.offer.task
        context["offer"] = self.offer
        context["contractor_view"] = self.request.user == self.offer.contractor
        context["form"] = self.form_class(**self.get_form_kwargs())
        context["attachment_form"] = self.attachment_form_class(prefix=self.prefix_form)
        return context

    def form_valid(self, form):
        """Save form, create solution object and assign it to the offer"""
        self.object = form.save()
        self.offer.solution = self.object
        self.offer.save()

    def attachment_form_valid(self, form):
        """Create solution attachment, assign it to solution and add attachment file from the from"""
        self.solution_attachment = SolutionAttachment(solution=self.object)
        self.solution_attachment.attachment = form.files["attachment_form-attachment"]
        self.solution_attachment.save()

    def post(self, request, *args, **kwargs):
        form = self.form_class(request.POST)
        if not form.is_valid():
            return self.form_invalid(form)
        self.form_valid(form)
        solution_attachment_form = self.attachment_form_class(request.POST, request.FILES, prefix=self.prefix_form)
        if solution_attachment_form.is_valid():
            self.attachment_form_valid(solution_attachment_form)
        return HttpResponseRedirect(self.get_success_url())


class SolutionDetailView(UserPassesTestMixin, DetailView):
    """
    This View displays solution details without possibility to edit anything
    """

    model = Solution
    redirect_url = reverse_lazy("dashboard")

    def test_func(self):
        solution = self.get_object()
        return self.request.user in [solution.offer.contractor, solution.offer.task.client]

    def handle_no_permission(self):
        if not self.request.user.is_authenticated:
            return super().handle_no_permission()
        return HttpResponseRedirect(SolutionDetailView.redirect_url)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["task"] = self.object.offer.task
        context["offer"] = self.object.offer
        context["attachments"] = self.object.attachments.all()
        context["is_contractor"] = self.request.user == self.object.offer.contractor
        context["is_client"] = self.request.user == self.object.offer.task.client
        context["attachments"] = self.object.attachments.all()
        return context


class SolutionEditView(UserPassesTestMixin, UpdateView):
    """
    This View allows to edit existing solution. This is the version of the view for the contractor
    """

    model = Solution
    form_class = SolutionForm

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.solution = None
        self.task = None

    def get_object(self):
        self.solution = super().get_object()
        self.task = self.solution.offer.task
        return self.solution

    def get_success_url(self):
        if self.request.user in [self.solution.offer.contractor, self.task.client]:
            return reverse("task-contractor-detail", kwargs={"pk": self.task.id})
        return reverse("dashboard")

    def test_func(self):
        self.get_object()
        user = self.request.user
        return user == self.solution.offer.contractor and not self.solution.accepted

    def handle_no_permission(self):
        if not self.request.user.is_authenticated:
            return super().handle_no_permission()
        return HttpResponseRedirect(self.get_success_url())

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["contractor_view"] = True
        context["task"] = self.object.offer.task
        context["offer"] = self.object.offer
        return context


class SolutionDeleteView(UserPassesTestMixin, DeleteView):
    """
    This view is used delete Solution. Only contractor can delete solution and only before it was accepted.
    """

    model = Solution
    template_name = "tasksapp/solution_confirm_delete.html"

    def get_success_url(self):
        solution = self.get_object()
        task = solution.offer.task
        return reverse("task-contractor-detail", kwargs={"pk": task.id})

    def test_func(self):
        solution = self.get_object()
        user = self.request.user
        return user == solution.offer.contractor and not solution.accepted

    def handle_no_permission(self):
        if not self.request.user.is_authenticated:
            return super().handle_no_permission()
        solution = self.get_object()
        task = solution.offer.task
        user = self.request.user
        if user == solution.offer.contractor:
            redirect_url = reverse("task-contractor-detail", kwargs={"pk": task.id})
        elif user == task.client:
            redirect_url = reverse("task-detail", kwargs={"pk": task.id})
        else:
            redirect_url = reverse("dashboard")
        return HttpResponseRedirect(redirect_url)
