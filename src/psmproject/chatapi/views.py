from chatapi.serializers import MessageListSerializer
from chatapp.models import Message
from django.contrib.auth.mixins import LoginRequiredMixin
from rest_framework.generics import ListAPIView


class MessageListApiView(LoginRequiredMixin, ListAPIView):
    model = Message
    serializer_class = MessageListSerializer

    def get_queryset(self):
        chat = self.kwargs["chat"]
        queryset = Message.objects.filter(chat=chat)
        return queryset
