from chatapp.models import Chat, Message, Participant, RoleChoices
from django.contrib.auth.models import User
from django.core.files.uploadedfile import SimpleUploadedFile
from factory import (
    Faker,
    PostGenerationMethodCall,
    Sequence,
    SubFactory,
    post_generation,
)
from factory.django import DjangoModelFactory
from tasksapp.models import (
    Complaint,
    ComplaintAttachment,
    Offer,
    Solution,
    SolutionAttachment,
    Task,
    TaskAttachment,
)
from usersapp.models import Skill


class UserFactory(DjangoModelFactory):
    class Meta:
        model = User

    username = Faker("user_name")
    email = Faker("email")
    password = PostGenerationMethodCall("set_password", "secret")
    first_name = Faker("first_name")
    last_name = Faker("last_name")


class SkillFactory(DjangoModelFactory):
    class Meta:
        model = Skill
        django_get_or_create = ["skill"]

    skill = Sequence(lambda n: f"Skill_{n}")


class TaskFactory(DjangoModelFactory):
    class Meta:
        model = Task

    title = Faker("word")
    description = Faker("text")
    realization_time = Faker("future_date")
    budget = Faker("pydecimal", left_digits=4, right_digits=2, positive=True)
    client = SubFactory(UserFactory)
    # status = Faker("random_int", min=0, max=5)

    @post_generation
    def skills(self, create, extracted, **kwargs):
        if not create:
            return

        if extracted:
            for skill in extracted:
                self.skills.add(skill)
        else:
            self.skills.add(SkillFactory())


class TaskAttachmentFactory(DjangoModelFactory):
    class Meta:
        model = TaskAttachment

    task = SubFactory(TaskFactory)
    attachment = SimpleUploadedFile(name="faker_filename.txt", content=b"content of test file")


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


class ComplaintFactory(DjangoModelFactory):
    class Meta:
        model = Complaint

    content = Faker("text")
    arbiter = SubFactory(UserFactory)
    task = SubFactory(TaskFactory)


class SolutionFactory(DjangoModelFactory):
    class Meta:
        model = Solution

    description = Faker("text")
    offer = SubFactory(OfferFactory)

    @classmethod
    def create(cls, **kwargs):
        solution = super().create(**kwargs)
        offer = kwargs.get("offer")
        if offer:
            offer.solution = solution
            offer.save()
        return solution


class SolutionAttachmentFactory(DjangoModelFactory):
    class Meta:
        model = SolutionAttachment

    solution = SubFactory(SolutionFactory)
    attachment = SimpleUploadedFile(name="faker_solution.txt", content=b"content of test file")


class ComplaintAttachmentFactory(DjangoModelFactory):
    class Meta:
        model = ComplaintAttachment

    complaint = SubFactory(ComplaintFactory)
    attachment = SimpleUploadedFile(name="faker_complaint.txt", content=b"content of test file")
