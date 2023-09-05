from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Q
from django.forms.models import model_to_dict
from django.http import HttpResponseRedirect
from django.views.generic.list import ListView
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

    PHRASE_KEY = "q"
    BUDGET_KEY = "budget"
    DATE_KEY = "date"
    SKILLS_KEY = "skills"
    SKILLS_DELIMITER = ","

    def get_queryset(self):
        phrase = self.request.GET.get(TasksSearchView.PHRASE_KEY, "")
        skills = self.request.GET.get(TasksSearchView.SKILLS_KEY, "")
        budget = self.request.GET.get(TasksSearchView.BUDGET_KEY, "")
        date = self.request.GET.get(TasksSearchView.DATE_KEY, "")
        queryset = Task.objects.exclude(Q(client=self.request.user) | Q(offers__contractor=self.request.user))
        if len(phrase) >= TasksSearchView.search_phrase_min:
            queryset = queryset.filter(Q(title__contains=phrase) | Q(description__contains=phrase))
        if skills:
            skills = skills.split(TasksSearchView.SKILLS_DELIMITER)
            skills_objects = skills_from_text(skills)
            print(skills_objects)
            queryset = queryset.filter(skills__in=skills_objects)
        return queryset

    def get_context_data(self, **kwargs):
        """Add skills list for skill selection to context,
        as well as skill prefix which is used to generate skill field names in form"""
        context = super().get_context_data(**kwargs)
        skills = Skill.objects.all()
        context["skills"] = [model_to_dict(skill) for skill in list(skills)]
        context["skill_id_prefix"] = SKILL_PREFIX
        return context

    def post(self, request, *args, **kwargs):
        my_url = request.path
        q = self.request.POST.get("q", "")
        skills = [item[1] for item in self.request.POST.items() if item[0].startswith(SKILL_PREFIX)]
        if q:
            my_url += f"?{TasksSearchView.PHRASE_KEY}={q}"
        if skills:
            skills_str = TasksSearchView.SKILLS_DELIMITER.join(skills)
            my_url += f"?{TasksSearchView.SKILLS_KEY}={skills_str}"

        return HttpResponseRedirect(my_url)
