from datetime import date, timedelta

from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.db import transaction
from django.db.models import Q
from django.forms.models import model_to_dict
from django.http import HttpResponseRedirect
from django.urls import reverse, reverse_lazy
from django.views.generic import View
from django.views.generic.edit import CreateView, UpdateView
from django.views.generic.list import ListView
from usersapp.helpers import skills_from_text
from usersapp.models import Skill

from ..forms.tasks import TaskForm, UpdateTaskForm
from ..models import Offer, Solution, Task


class TasksListBaseView(LoginRequiredMixin, ListView):
    """
    This is a base view class for displaying list of tasks created by currently logged-in user (client), ordered from
    newest. Tasks can be filtered by URL parameter "q". Search phrase will be compared against task title or task
    description. Result list is limited/paginated
    """

    model = Task
    template_name_suffix = "s_list"
    paginate_by = 10
    search_phrase_min = 3

    def get_queryset(self):
        phrase = self.request.GET.get("q", "")
        queryset = Task.objects.filter(client=self.request.user).order_by("-id")
        if len(phrase) >= TasksListBaseView.search_phrase_min:
            queryset = queryset.filter(Q(title__contains=phrase) | Q(description__contains=phrase))
        return queryset


class TasksCurrentListView(TasksListBaseView):
    """
    Extension of TasksListBaseView, displays only active tasks created by current user.
    """

    template_name_suffix = "s_list"

    def get_queryset(self):
        queryset = super().get_queryset()
        return queryset.filter(status__lt=Task.TaskStatus.COMPLETED)


class TasksHistoricalListView(TasksListBaseView):
    """
    Extension of TasksListBaseView, displays only historical tasks created by current user.
    """

    template_name_suffix = "s_history_list"

    def get_queryset(self):
        queryset = super().get_queryset()
        return queryset.filter(status__gte=Task.TaskStatus.COMPLETED)


SKILL_PREFIX = "task-skill-"


class TaskCreateView(LoginRequiredMixin, CreateView):
    """
    This View creates new tasks with logged-in user as a client
    """

    model = Task
    form_class = TaskForm
    success_url = reverse_lazy("tasks-client-list")

    def get_context_data(self, **kwargs):
        """Add skills list for skill selection to context,
        as well as skill prefix which is used to generate skill field names in form"""
        context = super().get_context_data(**kwargs)
        skills = Skill.objects.all()
        context["skills"] = [model_to_dict(skill) for skill in list(skills)]
        context["skill_id_prefix"] = SKILL_PREFIX
        return context

    def form_valid(self, form):
        """Assign current user to the new task and add skills"""
        form.instance.client = self.request.user
        response = super().form_valid(form)
        skills = [item[1] for item in self.request.POST.items() if item[0].startswith(SKILL_PREFIX)]
        if skills:
            skills_objects = skills_from_text(skills)
            self.object.skills.add(*skills_objects)
        return response


class TaskEditView(UserPassesTestMixin, UpdateView):
    """
    This View allows to edit existing task. Only client or moderator are allowed to edit.
    Task should be part of the URL
    """

    model = Task
    form_class = UpdateTaskForm

    def get_success_url(self):
        task = self.get_object()
        return reverse("task-detail", kwargs={"pk": task.id})

    def test_func(self):
        task = self.get_object()
        return task.client == self.request.user

    def handle_no_permission(self):
        return HttpResponseRedirect(self.get_success_url())

    def get_context_data(self, **kwargs):
        """Add skills of edited task and all possible skills to context data. Adds also skill_prefix which is used to
        generate skill field name in form"""
        context = super().get_context_data(**kwargs)
        skills = Skill.objects.all()
        if self.object:
            task_skills = self.object.skills.all()
            context["selected_skills"] = list(task_skills)
            skills = skills.difference(task_skills)
        context["skills"] = [model_to_dict(skill) for skill in list(skills)]
        context["skill_id_prefix"] = SKILL_PREFIX
        return context

    def form_valid(self, form):
        """Update/add skills after validating task form"""
        response = super().form_valid(form)
        skills = [item[1] for item in self.request.POST.items() if item[0].startswith(SKILL_PREFIX)]
        self.object.skills.clear()
        if skills:
            skills_objects = skills_from_text(skills)
            self.object.skills.add(*skills_objects)

        return response


class OfferClientListView(LoginRequiredMixin, ListView):
    """
    This is a view class for displaying list of offers for all tasks created by currently logged-in user (client),
    ordered by task from the newts. Offers can be filtered by URL parameter "q". Search phrase will be compared
    against offer description, task name, task description or contractor username. Result list is limited/paginated
    """

    model = Offer
    template_name_suffix = "s_list_client"
    paginate_by = 10
    search_phrase_min = 3

    def get_queryset(self):
        phrase = self.request.GET.get("q", "")
        queryset = (
            Offer.objects.filter(task__client=self.request.user)
            .order_by("-task__id", "-id")
            .filter(task__selected_offer=None)
        )
        if len(phrase) >= OfferClientListView.search_phrase_min:
            queryset = queryset.filter(
                Q(description__contains=phrase)
                | Q(task__title__contains=phrase)
                | Q(task__description__contains=phrase)
                | Q(contractor__username__contains=phrase)
            )
        return queryset


class TaskOfferClientListView(LoginRequiredMixin, ListView):
    """
    This is a view class for displaying list of offers for only one task. Offers are ordered by newest.
    Offers can be filtered by URL parameter "q". Search phrase will be compared against offer description
    and contractor username. Result list is limited/paginated
    """

    model = Offer
    template_name_suffix = "s_list_client_task"
    paginate_by = 10
    search_phrase_min = 3

    def get_queryset(self):
        task = Task.objects.get(id=self.kwargs["pk"])
        phrase = self.request.GET.get("q", "")
        queryset = Offer.objects.filter(task__id=task.id).order_by("-id")
        if len(phrase) >= TaskOfferClientListView.search_phrase_min:
            queryset = queryset.filter(Q(description__contains=phrase) | Q(contractor__username__contains=phrase))
        return queryset

    def get_context_data(self, **kwargs):
        """Add current task to the context"""
        context = super().get_context_data(**kwargs)
        context["task"] = Task.objects.get(id=self.kwargs["pk"])
        return context


class OfferClientAcceptView(UserPassesTestMixin, View):
    """
    This is a view class to accept offer by client. It change offer status to accepted, and change
    task status to on-going.
    """

    def dispatch(self, request, *args, **kwargs):
        offer = Offer.objects.get(id=self.kwargs["pk"])
        if offer.task.selected_offer is not None:
            messages.warning(self.request, "Task has already selected an offer")
            return HttpResponseRedirect(reverse("offers-client-list"))
        return super().dispatch(request, *args, **kwargs)

    def get_success_url(self):
        offer = Offer.objects.get(id=self.kwargs["pk"])
        return reverse("offer-detail", kwargs={"pk": offer.id})

    def test_func(self):
        offer = Offer.objects.get(id=self.kwargs["pk"])
        return self.request.user == offer.task.client

    def handle_no_permission(self):
        if not self.request.user.is_authenticated:
            return super().handle_no_permission()
        return HttpResponseRedirect(reverse("offers-client-list"))

    def post(self, request, *args, **kwargs):
        offer = Offer.objects.get(id=self.kwargs["pk"])
        if offer.task.selected_offer is not None:
            return HttpResponseRedirect(reverse("offers-client-list"))
        else:
            with transaction.atomic():
                offer.accepted = True
                offer.realization_time = date.today() + timedelta(days=offer.days_to_complete)
                offer.save()
                offer.task.selected_offer = offer
                offer.task.status = Task.TaskStatus.ON_GOING
                offer.task.save()
            return HttpResponseRedirect(self.get_success_url())


class SolutionClientAcceptView(UserPassesTestMixin, View):
    """
    This is a view class to accept solution by client. It change solution status to accepted, and change
    task status to complete.
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.object = None
        self.task = None

    def get_object(self):
        self.object = Solution.objects.get(id=self.kwargs["pk"])
        self.task = self.object.offer.task

    def dispatch(self, request, *args, **kwargs):
        self.get_object()
        return super().dispatch(request, *args, **kwargs)

    def get_success_url(self):
        return reverse("task-detail", kwargs={"pk": self.task.id})

    def test_func(self):
        return self.request.user == self.task.client

    def handle_no_permission(self):
        if not self.request.user.is_authenticated:
            return super().handle_no_permission()
        return HttpResponseRedirect(reverse("task-detail", kwargs={"pk": self.task.id}))

    def post(self, request, *args, **kwargs):
        with transaction.atomic():
            solution = self.object
            solution.accepted = True
            solution.save()
            self.task.status = Task.TaskStatus.COMPLETED
            self.task.save()
        return HttpResponseRedirect(self.get_success_url())
