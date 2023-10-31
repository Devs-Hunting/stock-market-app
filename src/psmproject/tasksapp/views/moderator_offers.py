import datetime

from django.db.models import Q
from django.urls import reverse
from django.views.generic.detail import DetailView
from django.views.generic.edit import UpdateView
from django.views.generic.list import ListView
from usersapp.helpers import ModeratorMixin

from ..forms.offers import OfferModeratorForm, OfferSearchForm
from ..models import Offer


class OfferListView(ModeratorMixin, ListView):
    """
    This is a view class for displaying list of all offers ordered from newest. It can only be used by administrator or
    moderator. Offers can be filtered by posted query. Search phrase will be compared against offer description,
    task name or task description. List can be filtered by accepted or not accepted offers. Parameter accepted can be
    also posted.
    Result list is limited/paginated
    """

    model = Offer
    template_name_suffix = "s_list_moderator"
    paginate_by = 10
    search_form_class = OfferSearchForm
    search_phrase_min = 3

    def get_queryset(self, **kwargs):
        """Get object list for a view and filter it if search form given"""
        queryset = Offer.objects.all().order_by("-id")
        form = kwargs.get("form")
        if not form:
            return queryset
        phrase = form.cleaned_data.get("query", "")
        if len(phrase) >= OfferListView.search_phrase_min:
            queryset = queryset.filter(
                Q(description__contains=phrase)
                | Q(task__title__contains=phrase)
                | Q(task__description__contains=phrase)
            )
        accepted = form.cleaned_data.get("accepted", False)
        queryset = queryset.filter(accepted=accepted)
        return queryset

    def get_context_data(self, **kwargs):
        """Create search form and add it to context"""
        context = super().get_context_data(**kwargs)
        if "form" in kwargs:
            context["form"] = kwargs.get("form")
            context["filtered"] = True
        else:
            context["form"] = OfferListView.search_form_class()
        return context

    def post(self, request, *args, **kwargs):
        form = OfferListView.search_form_class(request.POST)
        if not form.is_valid():
            return self.render_to_response(self.get_context_data())
        self.object_list = self.get_queryset(form=form)
        return self.render_to_response(self.get_context_data(form=form))


class OfferNewListView(ModeratorMixin, ListView):
    """
    This is a view class for displaying list of only newest offers. It can only be used by administrator, arbiter or
    moderator.
    Result list is limited/paginated
    """

    model = Offer
    template_name_suffix = "s_list_moderator"
    days = 3
    paginate_by = 10

    def get_queryset(self, **kwargs):
        """
        returns queryset of tasks not older than X days before. X is a class view parameter
        """
        search_start = datetime.datetime.now() - datetime.timedelta(days=OfferNewListView.days)
        queryset = Offer.objects.filter(created__gte=search_start).order_by("-id")
        return queryset


class OfferDetailView(ModeratorMixin, DetailView):
    """
    This View displays offer details without possibility to edit anything. Version for moderator
    """

    model = Offer
    template_name_suffix = "_detail_moderator"


class OfferEditView(ModeratorMixin, UpdateView):
    """
    This View allows to edit offer by the moderator or administrator. They can only edit description.
    """

    model = Offer
    form_class = OfferModeratorForm

    def get_success_url(self):
        offer = self.get_object()
        return reverse("offer-moderator-detail", kwargs={"pk": offer.id})
