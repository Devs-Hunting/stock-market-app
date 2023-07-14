from django.contrib.auth.models import User
from django.core.files.uploadedfile import SimpleUploadedFile
from factory import Faker, PostGenerationMethodCall, SubFactory
from factory.django import DjangoModelFactory
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


class TaskAttachmentFactory(DjangoModelFactory):
    class Meta:
        model = TaskAttachment

    task = SubFactory(TaskFactory)
    attachment = SimpleUploadedFile(str(Faker("file_name")), b"content of test file")
