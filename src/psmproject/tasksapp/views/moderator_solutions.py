import datetime

from django.db.models import Q
from django.urls import reverse
from django.views.generic.detail import DetailView
from django.views.generic.edit import UpdateView
from django.views.generic.list import ListView
from usersapp.helpers import ModeratorMixin

from ..forms.solution import SolutionModeratorForm, SolutionSearchForm
from ..models import Solution
from .common import SearchListView


class SolutionListView(ModeratorMixin, SearchListView):
    """
    This is a view class for displaying list of all solutions ordered from newest. It can only be used by administrator
    or moderator. Solutions can be filtered by posted query. Search phrase will be compared against solution description
    ,task name or task description. List can be filtered by accepted or not accepted solutions.
    Parameter accepted can be also posted.
    Result list is limited/paginated
    """

    model = Solution
    template_name_suffix = "s_list_moderator"
    paginate_by = 10
    search_form_class = SolutionSearchForm
    search_phrase_min = 3

    def search(self, queryset, form):
        """Get object list for a view and filter it if search form given"""
        phrase = form.cleaned_data.get("query", "")
        if len(phrase) >= SolutionListView.search_phrase_min:
            queryset = queryset.filter(
                Q(description__contains=phrase)
                | Q(offer__task__title__contains=phrase)
                | Q(offer__task__description__contains=phrase)
            )
        accepted = form.cleaned_data.get("accepted", False)
        queryset = queryset.filter(accepted=accepted)
        return queryset


class SolutionNewListView(ModeratorMixin, ListView):
    """
    This is a view class for displaying list of only newest solutions. It can only be used by administrator, arbiter or
    moderator.
    Result list is limited/paginated
    """

    model = Solution
    template_name_suffix = "s_list_moderator"
    days = 3
    paginate_by = 10

    def get_queryset(self, **kwargs):
        """
        returns queryset of tasks not older than X days before. X is a class view parameter
        """
        search_start = datetime.datetime.now() - datetime.timedelta(days=SolutionNewListView.days)
        queryset = Solution.objects.filter(updated_at__gte=search_start).order_by("-id")
        return queryset


class SolutionDetailView(ModeratorMixin, DetailView):
    """
    This View displays solution details without possibility to edit anything. Version for moderator.
    """

    model = Solution
    template_name_suffix = "_detail_moderator"


class SolutionEditView(ModeratorMixin, UpdateView):
    """
    This View allows to edit solution by the moderator or administrator. They can only edit description.
    """

    model = Solution
    form_class = SolutionModeratorForm

    def get_success_url(self):
        solution = self.get_object()
        return reverse("solution-moderator-detail", kwargs={"pk": solution.id})
