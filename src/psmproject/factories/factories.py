from chatapp.models import Chat, Message, Participant, RoleChoices
from django.contrib.auth.models import User
from django.core.files.uploadedfile import SimpleUploadedFile
from factory import Faker, PostGenerationMethodCall, SubFactory
from factory.django import DjangoModelFactory
from offerapp.models import Offer
from tasksapp.models import Task, TaskAttachment


class UserFactory(DjangoModelFactory):
    class Meta:
        model = User

    username = Faker("user_name")
    email = Faker("email")
    password = PostGenerationMethodCall("set_password", "secret")
    first_name = Faker("first_name")
    last_name = Faker("last_name")


class TaskFactory(DjangoModelFactory):
    class Meta:
        model = Task

    title = Faker("word")
    description = Faker("text")
    realization_time = Faker("future_date")
    budget = Faker("pydecimal", left_digits=4, right_digits=2, positive=True)
    client = SubFactory(UserFactory)
    # status = Faker("random_int", min=0, max=5)


class TaskAttachmentFactory(DjangoModelFactory):
    class Meta:
        model = TaskAttachment

    task = SubFactory(TaskFactory)
    attachment = SimpleUploadedFile(str(Faker("file_name")), b"content of test file")


class ChatFactory(DjangoModelFactory):
    class Meta:
        model = Chat


class TaskChatFactory(ChatFactory):
    content_object = SubFactory(TaskFactory)


class ChatParticipantFactory(DjangoModelFactory):
    class Meta:
        model = Participant

    user = SubFactory(UserFactory)
    chat = SubFactory(ChatFactory)


class TaskChatParticipantFactory(ChatParticipantFactory):
    role = Faker("random_element", elements=RoleChoices)


class MessageFactory(DjangoModelFactory):
    class Meta:
        model = Message

    chat = SubFactory(ChatFactory)
    author = SubFactory(UserFactory)
    content = Faker("text")


class OfferFactory(DjangoModelFactory):
    class Meta:
        model = Offer

    description = Faker("text")
    realization_time = Faker("future_date")
    budget = Faker("pydecimal", left_digits=4, right_digits=2, positive=True)
    contractor = SubFactory(UserFactory)
    task = SubFactory(TaskFactory)
