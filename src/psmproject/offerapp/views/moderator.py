from django.conf import settings
from django.contrib.auth.mixins import UserPassesTestMixin
from django.db.models import Q
from django.http import HttpResponseRedirect
from django.urls import reverse_lazy
from django.views.generic.list import ListView

from ..forms import OfferSearchForm
from ..models import Offer


class OfferListView(UserPassesTestMixin, ListView):
    """
    This is a view class for displaying list of all offers ordered from newest. It can only be used by administrator or
    moderator. Offers can be filtered by URL parameter "q". Search phrase will be compared against offer description,
    task name or task description.
    Result list is limited/paginated
    """

    model = Offer
    template_name_suffix = "s_list_all"
    allowed_groups = [
        settings.GROUP_NAMES.get("ADMINISTRATOR"),
        settings.GROUP_NAMES.get("MODERATOR"),
    ]
    redirect_url = reverse_lazy("dashboard")
    paginate_by = 10
    search_form_class = OfferSearchForm
    search_phrase_min = 3

    def get_queryset(self, **kwargs):
        """Get object list for a view and filter it if search form given"""
        queryset = Offer.objects.all()
        print(queryset)
        form = kwargs.get("form")
        if not form:
            return queryset.order_by("-id")

        phrase = form.cleaned_data.get("query", "")
        if len(phrase) >= OfferListView.search_phrase_min:
            queryset = queryset.filter(
                Q(description__contains=phrase)
                | Q(task__title__contains=phrase)
                | Q(task__description__contains=phrase)
            )
        accepted = form.cleaned_data.get("accepted", "")
        if accepted is not None:
            queryset = queryset.filter(accepted=accepted)
        return queryset

    def get_context_data(self, **kwargs):
        """Create search form and add it to context"""
        context = super().get_context_data(**kwargs)
        context["form"] = kwargs.get("form") if "form" in kwargs else OfferListView.search_form_class()
        return context

    def test_func(self):
        """Test if user has permission to load this view. Only member of allowed groups is granted permission"""
        user = self.request.user
        return user.groups.filter(name__in=OfferListView.allowed_groups).exists()

    def handle_no_permission(self):
        return HttpResponseRedirect(OfferListView.redirect_url)

    def post(self, request, *args, **kwargs):
        form = OfferListView.search_form_class(request.POST)
        if not form.is_valid():
            return self.render_to_response(self.get_context_data())
        self.object_list = self.get_queryset(form=form)
        return self.render_to_response(self.get_context_data(form=form))
