from chatapp.models import Message
from rest_framework.serializers import ModelSerializer


class MessageListSerializer(ModelSerializer):
    class Meta:
        model = Message
        fields = ["author", "content", "timestamp"]
