from chatapp.views import ChatView
from django.urls import path

urlpatterns = [path("<pk>", ChatView.as_view(), name="chat")]
