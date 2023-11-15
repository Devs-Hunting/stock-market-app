from django.conf import settings
from django.db.models import Q
from django.views.generic.list import ListView
from usersapp.helpers import ModeratorMixin

from ..forms.complaint import ComplaintSearchForm
from ..models import Complaint
from .common import SearchListView


class ComplaintListView(ModeratorMixin, SearchListView):
    """
    This is a view class for displaying list of all complaints of the arbiter ordered from newest. It can only be used
    by administrator or arbiter. Complaint can be filtered by posted query. Search phrase will be compared against
    complaint content, task name or task description. List can be filtered by closed status of the complaint or if
    there is assignet arbiter for it. Parameter accepted can be also posted.
    Result list is limited/paginated
    """

    model = Complaint
    template_name_suffix = "s_list_arbiter"
    paginate_by = 10
    search_form_class = ComplaintSearchForm
    search_phrase_min = 3
    allowed_groups = [settings.GROUP_NAMES.get("ADMINISTRATOR"), settings.GROUP_NAMES.get("ARBITER")]

    def get_queryset(self, **kwargs):
        """
        returns queryset of complaints of which current user is the arbiter
        """
        queryset = Complaint.objects.filter(arbiter=self.request.user).order_by("-id")
        form = kwargs.get("form")
        if not form or not form.is_valid():
            return queryset
        queryset = self.search(queryset, form)
        return queryset

    def search(self, queryset, form):
        """
        search method
        """
        phrase = form.cleaned_data.get("query", "")
        if len(phrase) >= ComplaintListView.search_phrase_min:
            queryset = queryset.filter(
                Q(content__contains=phrase) | Q(task__title__contains=phrase) | Q(task__description__contains=phrase)
            )
        closed = form.cleaned_data.get("closed", False)
        queryset = queryset.filter(accepted=closed)
        not_taken = not form.cleaned_data.get("taken", False)
        queryset = queryset.filter(arbiter__isnull=not_taken)
        date_start = form.cleaned_data.get("date_start")
        if date_start:
            queryset = queryset.filter(updated_at__gte=date_start)
        date_end = form.cleaned_data.get("date_end")
        if date_end:
            queryset = queryset.filter(updated_at__gte=date_end)
        return queryset


class ComplaintNewListView(ModeratorMixin, ListView):
    """
    This is a view class for displaying list of only not taken complaints. Can be used by administrator or arbiter
    Result list is limited/paginated
    """

    model = Complaint
    template_name_suffix = "s_list_arbiter"
    paginate_by = 10
    allowed_groups = [settings.GROUP_NAMES.get("ADMINISTRATOR"), settings.GROUP_NAMES.get("ARBITER")]

    def get_queryset(self, **kwargs):
        """
        returns queryset of complaints that don't have arbiter assigned and are not closed. Order from the newest
        """
        queryset = Complaint.objects.filter(Q(arbiter__isnull=True) & Q(closed=False)).order_by("-id")
        return queryset


class ComplaintActiveListView(ModeratorMixin, ListView):
    """
    This is a view class for displaying list of complaints taken by the arbiter that are not closed yet
    """

    model = Complaint
    template_name_suffix = "s_list_arbiter"
    paginate_by = 10
    allowed_groups = [settings.GROUP_NAMES.get("ADMINISTRATOR"), settings.GROUP_NAMES.get("ARBITER")]

    def get_queryset(self, **kwargs):
        """
        returns queryset of complaints that don't have arbiter assigned and are not closed. Order from the newest
        """
        queryset = Complaint.objects.filter(Q(arbiter=self.request.user) & Q(closed=False)).order_by("-id")
        return queryset
