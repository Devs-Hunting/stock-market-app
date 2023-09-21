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
from offerapp.forms import OfferForm, TaskSearchForm
from offerapp.models import Offer
from tasksapp.models import Task
from usersapp.helpers import skills_from_text
from usersapp.models import Skill

SKILL_PREFIX = "query-skill-"


class TasksSearchView(LoginRequiredMixin, ListView):
    """
    This is a search task list view for contractor to find new to tasks for an offer. \
    Tasks can be filtered by URL parameter "q". Search phrase will be compared against task title or task
    description. Tasks can also be filtered by skills, budget end end-date. Result list is limited/paginated.
    """

    model = Task
    template_name = "offerapp/task_search.html"
    paginate_by = 10
    search_phrase_min = 3

    def get_queryset(self, **kwargs):
        queryset = Task.objects.exclude(Q(client=self.request.user) | Q(offers__contractor=self.request.user))
        form = kwargs.get("form")
        if not form:
            return queryset.order_by("-id")

        phrase = form.cleaned_data.get("query", "")
        budget = form.cleaned_data.get("budget")
        date = form.cleaned_data.get("realization_time")
        selected_skills = kwargs.get("selected_skills")

        if len(phrase) >= TasksSearchView.search_phrase_min:
            queryset = queryset.filter(Q(title__contains=phrase) | Q(description__contains=phrase))
        if budget:
            queryset = queryset.filter(budget__gte=budget).distinct()
        if date:
            queryset = queryset.filter(realization_time__gte=date).distinct()
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

        context["form"] = kwargs.get("form") if "form" in kwargs else TaskSearchForm()
        context["skills"] = [model_to_dict(skill) for skill in list(skills)]
        context["skill_id_prefix"] = SKILL_PREFIX
        return context

    def post(self, request, *args, **kwargs):
        form = TaskSearchForm(request.POST)
        if not form.is_valid():
            return self.render_to_response(self.get_context_data())
        selected_skills = [item[1] for item in self.request.POST.items() if item[0].startswith(SKILL_PREFIX)]
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
                Q(description__contains=phrase) | Q(task__name__contains=phrase) | Q(task__description__contains=phrase)
            )
        return queryset


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
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["task"] = self.task
        return context

    def form_valid(self, form):
        """Assign current user and task to the new offer"""
        if not self.task:
            messages.warning(self.request, "task not found")
            return HttpResponseRedirect(self.get_success_url())
        form.instance.contractor = self.request.user
        form.instance.task = self.task
        return super().form_valid(form)


class OfferEditView(UserPassesTestMixin, UpdateView):
    """
    This View allows to edit existing offer. Only contractor or moderator are allowed to edit.
    """

    model = Offer
    allowed_groups = [
        settings.GROUP_NAMES.get("MODERATOR"),
    ]
    form_class = OfferForm

    def get_success_url(self):
        offer = self.get_object()
        return reverse("offer-detail", kwargs={"pk": offer.id})

    def test_func(self):
        offer = self.get_object()
        user = self.request.user
        in_allowed_group = user.groups.filter(name__in=OfferEditView.allowed_groups).exists()
        return user == offer.contractor or in_allowed_group

    def handle_no_permission(self):
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
    template_name = "offerapp/offer_confirm_delete.html"

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
        redirect_url = self.get_success_url()
        return HttpResponseRedirect(redirect_url)
