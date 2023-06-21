from django.contrib import admin
from django.contrib.auth import views as auth_views
from django.urls import path
from usersapp import views

urlpatterns = [
    path("admin/", admin.site.urls),
    path("register/", views.SignUpView.as_view(), name="register"),
    path("profile/", views.ProfileView.as_view(), name="profile"),
    path(
        "login/",
        auth_views.LoginView.as_view(template_name="usersapp/login.html"),
        name="login",
    ),
    path(
        "logout/",
        auth_views.LogoutView.as_view(template_name="usersapp/logout.html"),
        name="logout",
    ),
]
