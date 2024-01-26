from dashboardapp import views
from django.urls import include  # noqa
from django.urls import path

urlpatterns = [
    path("", views.DashboardView.as_view(), name="dashboard"),
    path("moderator", views.DashboardModeratorView.as_view(), name="dashboard-moderator"),
    path("arbiter", views.DashboardArbiterView.as_view(), name="dashboard-arbiter"),
    path("admin", views.DashboardAdminView.as_view(), name="dashboard-admin"),
]
