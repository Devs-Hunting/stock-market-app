from django.urls import path
from django.urls import include
from dashboardapp import views

urlpatterns = [
    path("", views.DashboardView.as_view(), name="dashboard"),
]
