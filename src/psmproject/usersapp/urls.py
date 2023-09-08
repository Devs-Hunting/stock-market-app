from django.contrib import admin
from django.urls import include, path
from usersapp import views

urlpatterns = [
    path("admin/", admin.site.urls),
    path("profile/", views.ProfileView.as_view(), name="profile"),
    path("accounts/", include("allauth.urls")),
    path("set_role/<role_id>", views.SetRoleView.as_view(), name="set-role"),
]
