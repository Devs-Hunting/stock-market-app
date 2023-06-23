from django.contrib import admin
from django.urls import path, include
from usersapp import views

urlpatterns = [
    path("admin/", admin.site.urls),
    path("profile/", views.ProfileView.as_view(), name="profile"),
    path("accounts/", include("allauth.urls")),
]
