from dashboardapp import views
from django.urls import include  # noqa
from django.urls import path

urlpatterns = [
    path("", views.DashboardView.as_view(), name="dashboard"),
]
