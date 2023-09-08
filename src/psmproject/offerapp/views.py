from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Q
from django.forms.models import model_to_dict
from django.views.generic.list import ListView
from tasksapp.models import Task
from usersapp.helpers import skills_from_text
from usersapp.models import Skill

from .forms import TaskSearchForm

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
            queryset = queryset.filter(budget__gte=budget)
        if date:
            queryset = queryset.filter(realization_time__gte=date)
        if selected_skills:
            queryset = queryset.filter(skills__in=selected_skills).distinct()
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
