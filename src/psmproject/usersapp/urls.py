from django.contrib import admin
from django.urls import include, path
from usersapp import views

urlpatterns = [
    path("admin/", admin.site.urls),
    path("profile/", views.ProfileView.as_view(), name="profile"),
    path("accounts/", include("allauth.urls")),
    path("set_role/<role_id>", views.SetRoleView.as_view(), name="set-role"),
    path("block_user/", views.BlockUserView.as_view(), name="block-user"),
    path("block_user/<int:pk>", views.BlockedUserDetailView.as_view(), name="blocked-user-detail"),
    path("blocked_users/", views.BlockedUsersListView.as_view(), name="blocked-users-list"),
]
