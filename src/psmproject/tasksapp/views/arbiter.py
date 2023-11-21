from django.conf import settings
from django.contrib.auth.mixins import UserPassesTestMixin
from django.db.models import Q
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.views.generic import View
from django.views.generic.detail import DetailView
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
        queryset = queryset.filter(closed=closed)
        not_taken = not form.cleaned_data.get("taken", False)
        queryset = queryset.filter(arbiter__isnull=not_taken)
        date_start = form.cleaned_data.get("date_start")
        if date_start:
            queryset = queryset.filter(updated_at__gte=date_start)
        date_end = form.cleaned_data.get("date_end")
        if date_end:
            queryset = queryset.filter(updated_at__lte=date_end)
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


class ComplaintDetailView(ModeratorMixin, DetailView):
    """
    Detail view for a complaint with all attachments. Version for arbiter
    """

    model = Complaint
    allowed_groups = [settings.GROUP_NAMES.get("ADMINISTRATOR"), settings.GROUP_NAMES.get("ARBITER")]
    template_name_suffix = "detail_arbiter"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["attachments"] = self.object.attachments.all()
        context["is_arbiter"] = self.request.user == self.object.arbiter
        return context


class ComplaintTakeView(ModeratorMixin, View):
    """
    This is a view class to take complaint by arbiter. It will have effect only if there is no arbiter assignet yet.
    """

    allowed_groups = [settings.GROUP_NAMES.get("ADMINISTRATOR"), settings.GROUP_NAMES.get("ARBITER")]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.object = None

    def get_object(self):
        self.object = Complaint.objects.get(id=self.kwargs["pk"])

    def get_success_url(self):
        return reverse("complaint-arbiter-detail", kwargs={"pk": self.object.id})

    def post(self, request, *args, **kwargs):
        self.get_object()
        if not self.object.arbiter:
            self.object.arbiter = request.user
            self.object.save()
        return HttpResponseRedirect(self.get_success_url())


class ComplaintCloseView(UserPassesTestMixin, View):
    """
    This is a view class to close complaint by arbiter. Only assigned arbiter can close it.
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.object = None

    def get_object(self):
        self.object = Complaint.objects.get(id=self.kwargs["pk"])
        return self.object

    def test_func(self):
        complaint = self.get_object()
        user = self.request.user
        return user == complaint.arbiter

    def get_success_url(self):
        return reverse("complaint-arbiter-detail", kwargs={"pk": self.object.id})

    def handle_no_permission(self):
        if not self.request.user.is_authenticated:
            return super().handle_no_permission()
        return HttpResponseRedirect(self.get_success_url())

    def post(self, request, *args, **kwargs):
        self.object.closed = True
        self.object.save()
        return HttpResponseRedirect(self.get_success_url())
