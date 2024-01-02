import os
import shutil
from datetime import datetime, timedelta

from django.conf import settings
from django.contrib.auth.models import Group
from django.test import Client, TestCase
from django.urls import reverse
from factories.factories import (
    OfferFactory,
    SolutionFactory,
    TaskAttachmentFactory,
    TaskFactory,
    UserFactory,
)
from tasksapp.models import ATTACHMENTS_PATH, Offer, Solution, Task, TaskAttachment
from tasksapp.views.contractor import SKILL_PREFIX
from usersapp.models import Skill

client = Client()


class TestContractorOfferListView(TestCase):
    """
    Test case for the contractor offer list view.
    """

    url_name = "offers-list"

    def setUp(self) -> None:
        """
        Set up method that is run before every individual test. Here it prepares test user and offers,
        logs in a user, and sets up a standard response object for use in the tests.
        """
        super().setUp()
        self.user = UserFactory.create()
        self.client_user = UserFactory.create()
        self.test_task1 = TaskFactory.create(client=self.client_user, title="UniqueTitle1")
        self.test_task2 = TaskFactory.create(client=self.client_user, title="UniqueTitle2")
        self.test_offer1 = OfferFactory.create(
            contractor=self.user, task=self.test_task1, description="very unique description for this object"
        )
        self.test_offer2 = OfferFactory.create(
            contractor=self.user, task=self.test_task2, description="totally different text then in the first one"
        )

        self.client.login(username=self.user.username, password="secret")
        self.url = reverse(TestContractorOfferListView.url_name)
        self.response = self.client.get(self.url)

    def tearDown(self):
        """
        Clean up method after each test case.
        """
        Task.objects.all().delete()
        Offer.objects.all().delete()
        super().tearDown()

    def test_should_return_status_code_200_when_request_by_name(self):
        """
        Test whether the view returns a HTTP 200 OK status code when a request is made.
        """
        self.assertEqual(self.response.status_code, 200)

    def test_should_check_that_view_use_correct_template(self):
        """
        Test whether the view uses the correct template.
        """
        self.assertEqual(self.response.status_code, 200)
        self.assertTemplateUsed(self.response, "tasksapp/offers_list.html")

    def test_should_return_correct_objects_when_request_is_sent(self):
        """
        Test whether the correct objects are returned when a request is sent to the view.
        """
        self.assertEqual(self.response.status_code, 200)
        self.assertTemplateUsed(self.response, "tasksapp/offers_list.html")
        self.assertEqual(
            list(self.response.context["object_list"]),
            [self.test_offer2, self.test_offer1],
        )

    def test_should_make_pagination_if_there_is_more_then_ten_element(self):
        """
        Test whether the view paginates the results when there are more than ten items.
        """
        for _ in range(11):
            temp_task = TaskFactory.create(client=self.client_user)
            OfferFactory.create(contractor=self.user, task=temp_task)

        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'href="?page=2"')
        self.assertEqual(len(response.context["object_list"]), 10)

    def test_should_redirect_if_not_logged_in(self):
        """
        Test whether the view correctly redirects to the login page if a not-logged-in user attempts to access it.
        """
        self.client.logout()
        self.response = self.client.get(self.url)
        self.assertRedirects(self.response, f"/users/accounts/login/?next={self.url}")

    def test_elements_should_be_sorted_by_id_from_newest(self):
        """
        Test whether the returned tasks are sorted by id from newest.
        """
        self.assertEqual(list(self.response.context["object_list"])[0], self.test_offer2)

    def test_should_return_objects_filtered_by_phrase_in_task_title(self):
        """
        Test whether the view returns offers filtered by a phrase present in the task title.
        """

        filter_word = self.test_task2.title
        response_filter = self.client.get(reverse(TestContractorOfferListView.url_name), {"q": filter_word})
        self.assertQuerysetEqual(response_filter.context["object_list"], [self.test_offer2])

    def test_should_return_objects_filterd_by_phrases_in_task_description(self):
        """
        Test whether the view returns offers filtered by a phrase present in the task description.
        """
        filter_word = self.test_task2.description[0:10]

        response_filter = self.client.get(reverse(TestContractorOfferListView.url_name), {"q": filter_word})
        self.assertQuerysetEqual(response_filter.context["object_list"], [self.test_offer2])

    def test_should_return_objects_filterd_by_phrases_in_offer_description(self):
        """
        Test whether the view returns offers filtered by a phrase present in the offer description.
        """
        filter_word = self.test_offer2.description[0:10]

        response_filter = self.client.get(reverse(TestContractorOfferListView.url_name), {"q": filter_word})
        self.assertQuerysetEqual(response_filter.context["object_list"], [self.test_offer2])


class TestContractorTaskSearchView(TestCase):
    """
    Test case for the contractor task search view
    """

    url_name = "offer-task-search"
    template = "tasksapp/task_search.html"

    @classmethod
    def setUpClass(cls) -> None:
        super().setUpClass()
        skills = ["python", "django", "java script", "flask"]
        cls.skills = []
        for skill in skills:
            cls.skills.append(Skill.objects.create(skill=skill))
        cls.url = reverse(TestContractorTaskSearchView.url_name)

    def setUp(self) -> None:
        """
        Set up method that is run before every individual test. Here it prepares test user and tasks,
        logs in a user, and sets up a standard response object for use in the tests. Tasks 1-3 should be returned.
        Task 4 is a task for which an offer was made. Task 5 is a task created by current user. Tasks 1-3 are ordered
        by budget the smallest first. Tasks 1-3 are ordered by realization time, the latest first.
        """
        super().setUp()
        self.user = UserFactory.create()
        self.client_user = UserFactory.create()
        self.test_task1 = TaskFactory.create(
            client=self.client_user,
            title="UniqueTitle1",
            skills=[self.skills[0], self.skills[1]],
            budget=100.0,
            realization_time="2023-09-01",
        )
        self.test_task2 = TaskFactory.create(
            client=self.client_user,
            title="UniqueTitle2",
            skills=[self.skills[2]],
            budget=200.0,
            realization_time="2023-08-01",
        )
        self.test_task3 = TaskFactory.create(
            client=self.client_user,
            title="UniqueTitle3",
            skills=[self.skills[3]],
            budget=300.0,
            realization_time="2023-07-01",
        )
        self.test_task4 = TaskFactory.create(client=self.client_user, skills=[self.skills[2]])
        self.test_offer4 = OfferFactory.create(contractor=self.user, task=self.test_task4)
        self.test_task5 = TaskFactory.create(client=self.user, skills=[self.skills[3]])

        self.client.login(username=self.user.username, password="secret")

        self.response = self.client.get(self.url)

    @classmethod
    def tearDownClass(cls):
        Skill.objects.all().delete()
        super().tearDownClass()

    def tearDown(self):
        """
        Clean up method after each test case.
        """
        Task.objects.all().delete()
        Offer.objects.all().delete()
        super().tearDown()

    def test_should_return_status_code_200_when_request_by_name(self):
        """
        Test whether the view returns a HTTP 200 OK status code when a request is made.
        """
        self.assertEqual(self.response.status_code, 200)

    def test_should_check_that_view_use_correct_template(self):
        """
        Test whether the view uses the correct template.
        """
        self.assertEqual(self.response.status_code, 200)
        self.assertTemplateUsed(self.response, TestContractorTaskSearchView.template)

    def test_should_return_correct_objects_when_request_is_sent(self):
        """
        Test whether the correct objects are returned when a request is sent to the view. View should only return tasks
        that are created by other users and for which no current user has not made an offer yet
        """
        self.assertEqual(self.response.status_code, 200)
        self.assertTemplateUsed(self.response, TestContractorTaskSearchView.template)
        self.assertEqual(
            list(self.response.context["object_list"]),
            [self.test_task3, self.test_task2, self.test_task1],
        )

    def test_should_make_pagination_if_there_is_more_then_ten_element(self):
        """
        Test whether the view paginates the results when there are more than ten items.
        """
        for _ in range(11):
            TaskFactory.create(client=self.client_user)

        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'href="?page=2"')
        self.assertEqual(len(response.context["object_list"]), 10)

    def test_should_redirect_if_not_logged_in(self):
        """
        Test whether the view correctly redirects to the login page if a not-logged-in user attempts to access it.
        """
        self.client.logout()
        self.response = self.client.get(self.url)
        self.assertRedirects(self.response, "/users/accounts/login/?next=/tasks/offer/task-search")

    def test_elements_should_be_sorted_by_id_from_newest(self):
        """
        Test whether the returned tasks are sorted by id from newest.
        """
        self.assertEqual(list(self.response.context["object_list"])[0], self.test_task3)

    def test_should_return_all_context_information_on_get(self):
        skills = self.response.context.get("skills")
        self.assertIsNotNone(skills)
        form = self.response.context.get("form")
        self.assertIsNotNone(form)
        skill_prefix = self.response.context.get("skill_id_prefix")
        self.assertIsNotNone(skill_prefix)

    def test_should_return_only_tasks_with_status_open(self):
        """
        Test if the object list contains only tasks with status OPEN
        """
        self.test_task1.status = Task.TaskStatus.ON_GOING
        self.test_task1.save()
        self.response = self.client.get(self.url)

        self.assertEqual(
            list(self.response.context["object_list"]),
            [self.test_task3, self.test_task2],
        )

    def test_should_return_objects_filtered_by_title_when_query_sent(self):
        response = self.client.get(
            self.url,
            {
                "query": self.test_task1.title,
            },
        )
        self.assertQuerysetEqual(response.context["object_list"], [self.test_task1])

    def test_should_return_objects_filtered_by_description_when_query_sent(self):
        response = self.client.get(
            self.url,
            {
                "query": self.test_task1.description[:10],
            },
        )
        self.assertQuerysetEqual(response.context["object_list"], [self.test_task1])

    def test_should_return_objects_filtered_by_budget(self):
        """
        Test if response contains only tasks with minimum budget higher/equal than posted in filter
        """
        response = self.client.get(
            self.url,
            {
                "budget": self.test_task2.budget,
            },
        )
        self.assertQuerysetEqual(response.context["object_list"], [self.test_task3, self.test_task2])

    def test_should_return_objects_filtered_by_date(self):
        """
        Test if response contains only tasks with realization date later or same as posted in filter
        """

        response = self.client.get(
            self.url,
            {
                "realization_time": self.test_task2.realization_time,
            },
        )
        self.assertQuerysetEqual(response.context["object_list"], [self.test_task2, self.test_task1])

    def test_should_return_objects_filtered_by_skills(self):
        """
        Test if response contains only tasks that have all skills listed in post
        """

        response = self.client.get(
            self.url,
            {
                f"{SKILL_PREFIX}1": self.skills[0].skill,
                f"{SKILL_PREFIX}2": self.skills[1].skill,
            },
        )
        self.assertQuerysetEqual(response.context["object_list"], [self.test_task1])

    def test_should_return_skill_list_without_selected(self):
        response = self.client.get(
            self.url,
            {
                f"{SKILL_PREFIX}1": self.skills[0].skill,
                f"{SKILL_PREFIX}2": self.skills[1].skill,
            },
        )

        skills = response.context.get("skills")
        self.assertIsNotNone(skills)
        self.assertNotIn(self.skills[0].skill, skills)
        self.assertNotIn(self.skills[1].skill, skills)


class TestContractorOfferCreateView(TestCase):
    """
    Test case for the contractor's create view.
    """

    url_name = "offer-create"
    template = "tasksapp/offer_form.html"

    @classmethod
    def setUpClass(cls) -> None:
        super().setUpClass()
        skills = ["python", "django", "java script", "flask"]
        cls.skills = []
        for skill in skills:
            cls.skills.append(Skill.objects.create(skill=skill))

    def setUp(self) -> None:
        super().setUp()
        self.user = UserFactory.create()
        self.client.force_login(self.user)
        delta = timedelta(
            days=7,
        )
        realization_time = datetime.now() + delta

        self.data = {
            "description": "New offer 7620192",
            "realization_time": realization_time.strftime("%Y-%m-%d"),
            "budget": 1220.12,
        }
        self.client_user = UserFactory.create()
        self.test_task1 = TaskFactory.create(
            client=self.client_user,
        )
        self.url = reverse(TestContractorOfferCreateView.url_name, kwargs={"task_pk": self.test_task1.id})

    @classmethod
    def tearDownClass(cls):
        Skill.objects.all().delete()
        super().tearDownClass()

    def tearDown(self):
        """
        Clean up method after each test case.
        """
        Task.objects.all().delete()
        Offer.objects.all().delete()
        super().tearDown()

    def test_should_return_status_code_200_when_request_is_sent(self):
        """
        Test whether the view returns a HTTP 200 OK status code when a GET request is made.
        """
        response = self.client.get(self.url)

        self.assertEqual(response.status_code, 200)

    def test_should_return_all_context_information_on_get(self):
        response = self.client.get(self.url)
        form = response.context.get("form")
        self.assertIsNotNone(form)
        task = response.context.get("task")
        self.assertIsNotNone(task)

    def test_should_create_offer_object(self):
        """
        Test whether a new offer object is created after a POST request is made. New offer object must be related with
        the task given as an url argument. New offer must have logged in user as a contractor.
        """
        response = self.client.post(self.url, data=self.data, follow=True)

        self.assertEqual(response.status_code, 200)
        created_offer = Offer.objects.filter(description=self.data["description"]).first()
        self.assertIsNotNone(created_offer)
        self.assertEqual(created_offer.task.id, self.test_task1.id)
        self.assertEqual(created_offer.contractor, self.user)

    def test_should_redirect_if_not_existing_task_id_is_passed_as_an_url_argument(self):
        """
        Test if the views redirects and NOT create an offer for not existing task
        """
        test_task2 = TaskFactory.create(
            client=self.client_user,
        )
        wrong_task_id = test_task2.id
        test_task2.delete()

        url = reverse(TestContractorOfferCreateView.url_name, kwargs={"task_pk": wrong_task_id})
        count_start = Offer.objects.all().count()
        response = self.client.post(url, data=self.data, follow=True)
        count_after = Offer.objects.all().count()
        self.assertRedirects(response, reverse("offers-list"))
        self.assertEqual(count_after, count_start)

    def test_should_redirect_to_proper_url_after_success(self):
        """
        Test whether the view redirects to the correct URL after a successful task creation.
        """
        response = self.client.post(self.url, data=self.data, follow=True)

        self.assertRedirects(
            response,
            reverse("offers-list"),
            status_code=302,
            target_status_code=200,
            fetch_redirect_response=True,
        )

    def test_should_return_non_context_when_no_user_is_log_in(self):
        """
        Test whether the view correctly redirects to the login page when a non-logged-in user attempts to access it.
        """
        self.client.logout()
        response = self.client.get(self.url)
        self.assertRedirects(response, f"/users/accounts/login/?next=/tasks/offer/add/task/{self.test_task1.id}")


class TestContractorOfferEditView(TestCase):
    """
    Test case for the contractor's edit view.
    """

    url_name = "offer-edit"
    template = "tasksapp/offer_form.html"

    def setUp(self) -> None:
        super().setUp()
        self.user = UserFactory.create()
        self.client_user = UserFactory.create()
        self.test_task = TaskFactory.create(client=self.client_user)
        self.test_offer = OfferFactory.create(contractor=self.user, task=self.test_task)

        self.client.login(username=self.user.username, password="secret")
        self.url = reverse(TestContractorOfferEditView.url_name, kwargs={"pk": self.test_offer.id})

        delta = timedelta(
            days=2,
        )
        new_realization = datetime.now() + delta

        self.data = {
            "description": "New offer 7620192",
            "realization_time": new_realization.strftime("%Y-%m-%d"),
            "budget": 1220.12,
        }

    def tearDown(self):
        """
        Clean up method after each test case.
        """
        Task.objects.all().delete()
        Offer.objects.all().delete()
        super().tearDown()

    def test_should_return_status_code_200_when_request_is_sent(self):
        """
        Test whether the view returns a HTTP 200 OK status code when a GET request is made.
        """
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)

    def test_should_update_offer_object(self):
        """
        Test if the offer is correctly updated on post. Offer data must be updated and view redirects to detail view.
        """
        response = self.client.post(self.url, data=self.data)
        self.assertRedirects(response, reverse("offer-detail", kwargs={"pk": self.test_offer.pk}))
        self.test_offer.refresh_from_db()
        self.assertEqual(self.test_offer.description, self.data["description"])
        new_date = datetime.strptime(self.data["realization_time"], "%Y-%m-%d").date()
        self.assertEqual(self.test_offer.realization_time, new_date)
        self.assertEqual(float(self.test_offer.budget), self.data["budget"])

    def test_should_return_non_context_when_no_user_is_log_in(self):
        """
        Test whether the view correctly redirects to the login page when a non-logged-in user attempts to access it.
        """
        self.client.logout()
        response = self.client.get(self.url)
        self.assertRedirects(response, f"/users/accounts/login/?next={self.url}")

    def test_should_redirect_if_user_is_not_contractor(self):
        """
        Test if the client will be redirected if the current user is not contractor of the offer.
        """

        another_user = UserFactory.create()
        self.client.login(username=another_user.username, password="secret")
        response = self.client.get(self.url)
        self.assertRedirects(response, reverse("offer-detail", kwargs={"pk": self.test_offer.pk}))


class TestContractorOfferDetailView(TestCase):
    """
    Test case for the contractor's Offer Detail View
    """

    url_name = "offer-detail"
    template = "tasksapp/offer_detail.html"

    @classmethod
    def setUpClass(cls):
        """
        Set up data for the whole TestCase
        """
        super().setUpClass()
        cls.user = UserFactory.create()
        cls.client_user = UserFactory.create()
        cls.another_user = UserFactory.create()
        cls.test_task = TaskFactory.create(client=cls.client_user)
        cls.test_offer = OfferFactory.create(contractor=cls.user, task=cls.test_task)

        cls.url = reverse(TestContractorOfferDetailView.url_name, kwargs={"pk": cls.test_offer.id})

    def setUp(self) -> None:
        super().setUp()
        self.client.login(username=self.user.username, password="secret")
        self.response = self.client.get(self.url)

    @classmethod
    def tearDownClass(cls) -> None:
        Task.objects.all().delete()
        Offer.objects.all().delete()
        super().tearDownClass()

    def test_should_retrieve_offer_detail_with_valid_offer_id(self):
        """
        Test case to check if Offer Detail View works correctly with a valid task id
        """
        self.assertEqual(self.response.status_code, 200)
        self.assertTemplateUsed(self.response, TestContractorOfferDetailView.template)
        self.assertIn("object", self.response.context)
        self.assertEqual(self.response.context["object"], self.test_offer)

    def test_should_require_login_for_offer_detail(self):
        """
        Test case to check if Offer Detail View requires user login
        """
        self.client.logout()
        response = self.client.get(self.url)
        self.assertRedirects(response, f"/users/accounts/login/?next={self.url}")

    def test_should_return_all_context_information(self):
        """
        Test case to check if Offer Detail View return context information. Checks values depend on type of user
        logged in
        """
        self.assertEqual(self.response.context.get("is_contractor"), True)
        self.assertEqual(self.response.context.get("is_client"), False)

        self.client.login(username=self.client_user, password="secret")
        response = self.client.get(self.url)
        self.assertEqual(response.context.get("is_contractor"), False)
        self.assertEqual(response.context.get("is_client"), True)

        self.client.login(username=self.another_user, password="secret")
        response = self.client.get(self.url)
        self.assertEqual(response.context.get("is_contractor"), False)
        self.assertEqual(response.context.get("is_client"), False)


class TestContractorOfferDeleteView(TestCase):
    """
    Test case for the contractor's Offer Delete View
    """

    url_name = "offer-delete"
    template = "tasksapp/offer_confirm_delete.html"

    @classmethod
    def setUpClass(cls):
        """
        Set up data for the whole TestCase
        """
        super().setUpClass()
        cls.user = UserFactory.create()
        cls.client_user = UserFactory.create()
        cls.user_moderator = UserFactory.create()
        moderator_group, created = Group.objects.get_or_create(name=settings.GROUP_NAMES.get("MODERATOR"))
        cls.user_moderator.groups.add(moderator_group)
        cls.test_task = TaskFactory.create(client=cls.client_user)

    @classmethod
    def tearDownClass(cls) -> None:
        Task.objects.all().delete()
        super().tearDownClass()

    def setUp(self) -> None:
        super().setUp()
        self.test_offer = OfferFactory.create(contractor=self.user, task=self.test_task)
        self.url = reverse(TestContractorOfferDeleteView.url_name, kwargs={"pk": self.test_offer.id})
        self.client.login(username=self.user.username, password="secret")
        self.response = self.client.get(self.url)

    def tearDown(self) -> None:
        Offer.objects.all().delete()
        super().tearDown()

    def test_should_retrieve_offer_delete_confirmation_page_with_valid_offer_id(self):
        """
        Test checks if valid confirmation template with required information is returned on get
        """
        self.assertEqual(self.response.status_code, 200)
        self.assertTemplateUsed(self.response, TestContractorOfferDeleteView.template)
        self.assertIn("object", self.response.context)
        self.assertIn("form", self.response.context)
        self.assertEqual(self.response.context["object"], self.test_offer)

    def test_should_return_non_context_when_no_user_is_log_in(self):
        """
        Test whether the view correctly redirects to the login page when a non-logged-in user attempts to access it.
        """
        self.client.logout()
        response = self.client.get(self.url)
        self.assertRedirects(response, f"/users/accounts/login/?next={self.url}")

    def test_should_redirect_if_user_is_not_contractor_or_moderator(self):
        """
        Test if the client will be redirected if the current user is not contractor of the offer or moderator.
        """

        another_user = UserFactory.create()
        self.client.login(username=another_user.username, password="secret")
        response = self.client.get(self.url)
        self.assertRedirects(response, reverse("offers-list"))

    def test_should_allow_contractor_to_delete_unaccepted_offers(self):
        """
        Test case to check if contractor can delete offer before it is accepted
        """
        self.test_offer.accepted = False
        self.test_offer.save()

        response = self.client.post(self.url)
        self.assertEqual(response.status_code, 302)

        with self.assertRaises(Offer.DoesNotExist):
            Offer.objects.get(id=self.test_offer.id)

    def test_should_allow_moderator_to_delete_unaccepted_offers(self):
        """
        Test case to check if moderator can delete offer before it is accepted
        """
        self.test_offer.accepted = False
        self.test_offer.save()

        self.client.login(username=self.user_moderator.username, password="secret")
        response = self.client.post(self.url)
        self.assertEqual(response.status_code, 302)

        with self.assertRaises(Offer.DoesNotExist):
            Offer.objects.get(id=self.test_offer.id)

    def test_should_not_delete_accepted_offers(self):
        """
        Test case to check if contractor can delete offer before it is accepted
        """
        self.test_offer.accepted = True
        self.test_offer.save()

        response = self.client.post(self.url)
        self.assertRedirects(response, reverse("offers-list"))
        self.assertIsNotNone(Offer.objects.filter(id=self.test_offer.id).first())


class TestContractorTaskListView(TestCase):
    """
    Test case for the contractors tasks list view.
    """

    url_name = "tasks-contractor-list"
    template = "tasksapp/tasks_list_contractor.html"

    @classmethod
    def setUpClass(cls) -> None:
        """
        Set up method that is run before every individual test. Here it prepares test user, tasks and offers as well as
        url
        """
        super().setUpClass()
        cls.user = UserFactory.create()
        cls.client_user = UserFactory.create()
        cls.url = reverse("tasks-contractor-list")

    def setUp(self) -> None:
        """
        Set up method that is run before every individual test. Here it logs user in and sends request.
        """
        super().setUp()

        self.test_task1 = TaskFactory.create(client=self.client_user, title="mkdsakcnzx8213nmds")
        self.test_task2 = TaskFactory.create(client=self.client_user, title="kds99k,mck12")
        self.test_task3 = TaskFactory.create(client=self.client_user, title="dksjai1213")
        self.test_task4 = TaskFactory.create(client=self.client_user, title="kkkkkk1213210")
        self.test_offer1 = OfferFactory.create(contractor=self.user, task=self.test_task1)
        self.test_task1.selected_offer = self.test_offer1
        self.test_task1.status = Task.TaskStatus.ON_GOING
        self.test_task1.save()
        self.test_offer2 = OfferFactory.create(contractor=self.user, task=self.test_task2)
        self.test_task2.selected_offer = self.test_offer2
        self.test_task2.status = Task.TaskStatus.ON_GOING
        self.test_task2.save()
        self.test_offer3 = OfferFactory.create(contractor=self.user, task=self.test_task3)
        self.test_task3.selected_offer = self.test_offer3
        self.test_task3.status = Task.TaskStatus.COMPLETED
        self.test_task3.save()

        self.client.login(username=self.user.username, password="secret")
        self.response = self.client.get(self.url)

    def tearDown(self):
        """
        Clean up method after each test
        """
        Task.objects.all().delete()
        Offer.objects.all().delete()
        super().tearDown()

    def test_should_return_status_code_200_when_request_by_name(self):
        """
        Test whether the view returns a HTTP 200 OK status code when a request is made.
        """
        self.assertEqual(self.response.status_code, 200)

    def test_should_check_that_view_use_correct_template(self):
        """
        Test whether the view uses the correct template.
        """
        self.assertEqual(self.response.status_code, 200)
        self.assertTemplateUsed(self.response, TestContractorTaskListView.template)

    def test_should_return_correct_objects_when_request_is_sent(self):
        """
        Test whether the correct objects are returned when a request is sent to the view.
        """
        self.assertEqual(self.response.status_code, 200)
        self.assertTemplateUsed(self.response, TestContractorTaskListView.template)
        self.assertEqual(
            list(self.response.context["object_list"]),
            [self.test_task2, self.test_task1],
        )

    def test_should_make_pagination_if_there_is_more_then_ten_element(self):
        """
        Test whether the view paginates the results when there are more than ten items.
        """
        temp_tasks = []
        temp_offers = []

        for _ in range(11):
            temp_task = TaskFactory.create(client=self.client_user)
            temp_tasks.append(temp_task.id)
            temp_offer = OfferFactory.create(contractor=self.user, task=temp_task)
            temp_task.selected_offer = temp_offer
            temp_task.status = Task.TaskStatus.ON_GOING
            temp_task.save()
            temp_offers.append(temp_offer.id)

        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'href="?page=2"')
        self.assertEqual(len(response.context["object_list"]), 10)

    def test_should_redirect_if_not_logged_in(self):
        """
        Test whether the view correctly redirects to the login page if a not-logged-in user attempts to access it.
        """
        self.client.logout()
        self.response = self.client.get(self.url)
        self.assertRedirects(self.response, f"/users/accounts/login/?next={self.url}")

    def test_elements_should_be_sorted_by_id_from_newest(self):
        """
        Test whether the returned tasks are sorted by id from newest.
        """
        self.assertEqual(list(self.response.context["object_list"])[0], self.test_task2)

    def test_should_return_objects_filtered_by_phrase_in_task_title(self):
        """
        Test whether the view returns tasks filtered by a phrase present in the task title.
        """
        filter_word = self.test_task2.title
        response_filter = self.client.get(self.url, {"q": filter_word})
        self.assertQuerysetEqual(response_filter.context["object_list"], [self.test_task2])

    def test_should_return_objects_filterd_by_phrases_in_task_description(self):
        """
        Test whether the view returns tasks filtered by a phrase present in the task description.
        """
        filter_word = self.test_task2.description[0:10]
        response_filter = self.client.get(self.url, {"q": filter_word})
        self.assertQuerysetEqual(response_filter.context["object_list"], [self.test_task2])


class TestContractorTaskDetailView(TestCase):
    """
    Test case for the contractor's Task Detail View
    """

    url_name = "task-contractor-detail"
    template = "tasksapp/task_detail_contractor.html"

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = UserFactory()
        cls.test_task1 = TaskFactory(client=cls.user)
        cls.test_task2 = TaskFactory(client=cls.user)
        cls.test_attachment1 = TaskAttachmentFactory(task=cls.test_task1)
        cls.test_attachment2 = TaskAttachmentFactory(task=cls.test_task2)
        cls.url = reverse(TestContractorTaskDetailView.url_name, kwargs={"pk": cls.test_task1.id})

    def setUp(self):
        self.client.login(username=self.user.username, password="secret")
        self.response = self.client.get(self.url)

    @classmethod
    def tearDownClass(cls) -> None:
        Task.objects.all().delete()
        file_path = os.path.join(ATTACHMENTS_PATH)
        shutil.rmtree(file_path, ignore_errors=True)
        TaskAttachment.objects.all().delete()
        super().tearDownClass()

    def test_should_retrieve_task_detail_with_valid_task_id(self):
        """
        Test case to check if Task Detail View works correctly with a valid task id
        """

        self.assertEqual(self.response.status_code, 200)
        self.assertTemplateUsed(self.response, TestContractorTaskDetailView.template)
        self.assertIn("attachments", self.response.context)
        self.assertIn("task", self.response.context)
        self.assertEqual(self.response.context["task"], self.test_task1)

    def test_should_require_login_for_task_detail_access(self):
        """
        Test case to check if Task Detail View requires user login
        """
        self.client.logout()
        response = self.client.get(self.url)
        self.assertRedirects(response, f"/users/accounts/login/?next={self.url}")


class TestContractorSolutionCreateView(TestCase):
    """
    Test case for the contractor's solution create view.
    """

    url_name = "solution-create"
    template = "tasksapp/solution_form.html"

    @classmethod
    def setUpClass(cls) -> None:
        super().setUpClass()
        cls.contractor_user = UserFactory.create()
        cls.client_user = UserFactory.create()
        cls.test_task1 = TaskFactory.create(client=cls.client_user)
        cls.test_offer1 = OfferFactory.create(task=cls.test_task1, contractor=cls.contractor_user)
        cls.test_task1.selected_offer = cls.test_offer1
        cls.test_task1.status = Task.TaskStatus.ON_GOING
        cls.test_task1.save()

    def setUp(self) -> None:
        super().setUp()
        self.data = {
            "description": "New solution 987654321",
        }

        self.url = reverse(TestContractorSolutionCreateView.url_name, kwargs={"offer_pk": self.test_offer1.id})
        self.client.login(username=self.contractor_user.username, password="secret")
        self.response = self.client.get(self.url)

    @classmethod
    def tearDownClass(cls):
        Task.objects.all().delete()
        Offer.objects.all().delete()
        super().tearDownClass()

    def tearDown(self):
        """
        Clean up method after each test case.
        """
        Solution.objects.all().delete()
        super().tearDown()

    def test_should_return_status_code_200_when_request_is_sent(self):
        """
        Test whether the view returns a HTTP 200 OK status code when a GET request is made.
        """
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)

    def test_should_return_all_context_information_on_get(self):
        response = self.client.get(self.url)
        form = response.context.get("form")
        self.assertIsNotNone(form)
        task = response.context.get("task")
        self.assertIsNotNone(task)
        offer = response.context.get("offer")
        self.assertIsNotNone(offer)

    def test_should_create_solution_object(self):
        """
        Test whether a new solution object is created after a POST request is made. New solution object must be related
        with the offer given as an url argument. New offer must have logged in user as a contractor.
        """
        response = self.client.post(self.url, data=self.data, follow=True)

        self.assertEqual(response.status_code, 200)
        created_solution = Solution.objects.filter(description=self.data["description"]).first()
        self.assertIsNotNone(created_solution)
        self.assertEqual(created_solution.offer.id, self.test_offer1.id)
        self.test_offer1.refresh_from_db()
        self.assertEqual(self.test_offer1.solution.id, created_solution.id)

    def test_should_redirect_if_not_existing_offer_id_is_passed_as_an_url_argument(self):
        """
        Test if the views redirects and NOT create an solution for not existing offer
        """
        test_task2 = TaskFactory.create(
            client=self.client_user,
        )
        test_offer2 = OfferFactory.create(
            task=test_task2,
            contractor=self.contractor_user,
        )
        wrong_offer_id = test_offer2.id
        test_offer2.delete()
        test_task2.delete()

        count_start = Solution.objects.all().count()
        url = reverse(TestContractorSolutionCreateView.url_name, kwargs={"offer_pk": wrong_offer_id})
        response = self.client.post(url, data=self.data, follow=True)
        count_after = Solution.objects.all().count()
        self.assertRedirects(response, reverse("tasks-contractor-list"))
        self.assertEqual(count_after, count_start)

    def test_should_redirect_if_offer_already_has_solution(self):
        """
        Test if the views redirects and not create solution if there is already solution for the offer
        """
        existing_solution = SolutionFactory.create(offer=self.test_offer1)
        self.test_offer1.solution = existing_solution
        self.test_offer1.save()
        count_start = Solution.objects.all().count()
        response = self.client.post(self.url, data=self.data, follow=True)
        count_after = Solution.objects.all().count()
        self.assertRedirects(response, reverse("tasks-contractor-list"))
        self.assertEqual(count_after, count_start)

    def test_should_redirect_to_proper_url_after_success(self):
        """
        Test whether the view redirects to the correct URL after a successful solution creation.
        """
        response = self.client.post(self.url, data=self.data, follow=True)

        self.assertRedirects(
            response,
            reverse("task-contractor-detail", kwargs={"pk": self.test_task1.id}),
            status_code=302,
            target_status_code=200,
            fetch_redirect_response=True,
        )

    def test_should_redirect_when_user_is_not_logged_in(self):
        """
        Test whether the view correctly redirects to the login page when a non-logged-in user attempts to access it.
        """
        self.client.logout()
        response = self.client.get(self.url)
        self.assertRedirects(response, f"/users/accounts/login/?next={self.url}")

    def test_should_redirect_if_user_is_not_contractor(self):
        """
        Test whether the view correctly redirects if user is not a contractor for the offer.
        """
        self.client.logout()
        another_user = UserFactory.create()
        self.client.login(username=another_user.username, password="secret")
        response = self.client.get(self.url)
        self.assertRedirects(response, reverse("tasks-contractor-list"))


class TestContractorSolutionDetailView(TestCase):
    """
    Test case for the contractor's Solution Detail View
    """

    url_name = "solution-detail"
    template = "tasksapp/solution_detail.html"

    @classmethod
    def setUpClass(cls):
        """
        Set up data for the whole TestCase
        """
        super().setUpClass()
        cls.user = UserFactory.create()
        cls.client_user = UserFactory.create()
        cls.another_user = UserFactory.create()
        cls.test_task = TaskFactory.create(client=cls.client_user)
        cls.test_offer = OfferFactory.create(contractor=cls.user, task=cls.test_task)
        cls.test_solution = SolutionFactory()
        cls.test_offer.solution = cls.test_solution
        cls.test_offer.save()
        cls.url = reverse(TestContractorSolutionDetailView.url_name, kwargs={"pk": cls.test_solution.id})

    def setUp(self) -> None:
        super().setUp()
        self.client.login(username=self.user.username, password="secret")
        self.response = self.client.get(self.url)

    @classmethod
    def tearDownClass(cls) -> None:
        Solution.objects.all().delete()
        Offer.objects.all().delete()
        Task.objects.all().delete()
        super().tearDownClass()

    def test_should_retrieve_solution_detail_with_valid_offer_id(self):
        """
        Test case to check if Solution Detail View works correctly with a valid id
        """
        self.assertEqual(self.response.status_code, 200)
        self.assertTemplateUsed(self.response, TestContractorSolutionDetailView.template)
        self.assertIn("object", self.response.context)
        self.assertEqual(self.response.context["object"], self.test_solution)

    def test_should_require_login_for_solution_detail(self):
        """
        Test case to check if Solution Detail View requires user login
        """
        self.client.logout()
        response = self.client.get(self.url)
        self.assertRedirects(response, f"/users/accounts/login/?next={self.url}")

    def test_should_return_all_context_information(self):
        """
        Test case to check if Solution Detail View return context information. Checks values depend on type of user
        logged in
        """
        self.assertIn("task", self.response.context)
        self.assertIn("offer", self.response.context)
        self.assertEqual(self.response.context.get("is_contractor"), True)
        self.assertEqual(self.response.context.get("is_client"), False)

        self.client.login(username=self.client_user, password="secret")
        response = self.client.get(self.url)
        self.assertEqual(response.context.get("is_contractor"), False)
        self.assertEqual(response.context.get("is_client"), True)

    def test_should_redirect_if_user_is_not_client_or_contractor(self):
        """
        Test if the client will be redirected if the current user is not contractor or client of the task.
        """

        another_user = UserFactory.create()
        self.client.login(username=another_user.username, password="secret")
        response = self.client.get(self.url)
        self.assertRedirects(response, reverse("dashboard"))


class TestContractorSolutionEditView(TestCase):
    """
    Test case for the contractor's solution edit view.
    """

    url_name = "solution-edit"
    template = "tasksapp/solution_form.html"

    def setUp(self) -> None:
        super().setUp()
        self.user = UserFactory.create()
        self.client_user = UserFactory.create()
        self.test_task = TaskFactory.create(client=self.client_user)
        self.test_offer = OfferFactory.create(contractor=self.user, task=self.test_task)
        self.test_solution = SolutionFactory.create()
        self.test_offer.solution = self.test_solution
        self.test_offer.save()

        self.client.login(username=self.user.username, password="secret")
        self.url = reverse(TestContractorSolutionEditView.url_name, kwargs={"pk": self.test_solution.id})

        self.data = {
            "description": "New description made just now. It is describing the solution given by the contractor",
        }

    def tearDown(self):
        """
        Clean up method after each test case.
        """
        Solution.objects.all().delete()
        Offer.objects.all().delete()
        Task.objects.all().delete()
        super().tearDown()

    def test_should_return_status_code_200_when_request_is_sent(self):
        """
        Test whether the view returns a HTTP 200 OK status code when a GET request is made.
        """
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)

    def test_should_return_all_context_information(self):
        """
        Test case to check if Solution Detail View return context information. Checks values depend on type of user
        logged in
        """
        response = self.client.get(self.url)
        self.assertIn("task", response.context)
        self.assertIn("offer", response.context)
        self.assertIn("form", response.context)
        self.assertIn("object", response.context)

    def test_should_update_solution_object(self):
        """
        Test if the solution is correctly updated on post. Solution data must be updated and view redirects to detail
        view.
        """
        response = self.client.post(self.url, data=self.data, follow=True)

        self.assertRedirects(response, reverse("task-contractor-detail", kwargs={"pk": self.test_task.pk}))
        self.test_solution.refresh_from_db()
        self.assertEqual(self.test_solution.description, self.data["description"])

    def test_should_redirect_when_no_user_is_log_in(self):
        """
        Test whether the view correctly redirects to the login page when a non-logged-in user attempts to access it.
        """
        self.client.logout()
        response = self.client.get(self.url)
        self.assertRedirects(response, f"/users/accounts/login/?next={self.url}")

    def test_should_redirect_accepted_solution(self):
        """
        Test case to check if accepted solution cannot be edited
        """

        self.test_solution.accepted = True
        self.test_solution.save()
        response = self.client.get(self.url)

        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse("task-contractor-detail", kwargs={"pk": self.test_task.pk}))

    def test_should_not_update_accepted_solution_object(self):
        """
        Test if the accepted solution is not updated on post.
        """
        self.test_solution.accepted = True
        self.test_solution.save()
        response = self.client.post(self.url, data=self.data, follow=True)

        self.assertRedirects(response, reverse("task-contractor-detail", kwargs={"pk": self.test_task.pk}))
        test_solution_after = Solution.objects.filter(pk=self.test_solution.pk).first()
        self.assertEqual(self.test_solution.description, test_solution_after.description)

    def test_should_redirect_if_user_is_not_contractor(self):
        """
        Test if the client will be redirected if the current user is not contractor of the solution. Client will be
        redirected to task detail view and another user to the dashboard.
        """
        self.client.login(username=self.client_user.username, password="secret")
        response = self.client.get(self.url)
        self.assertRedirects(response, reverse("task-contractor-detail", kwargs={"pk": self.test_task.pk}))

        another_user = UserFactory.create()
        self.client.login(username=another_user.username, password="secret")
        response = self.client.get(self.url, follow=True)
        self.assertRedirects(response, reverse("dashboard"))


class TestSolutionDeleteView(TestCase):
    """
    Test case for the Solution Delete View
    """

    url_name = "solution-delete"

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = UserFactory.create()
        cls.client_user = UserFactory.create()
        cls.test_task = TaskFactory.create(client=cls.client_user)
        cls.test_offer = OfferFactory.create(contractor=cls.user, task=cls.test_task)

    def setUp(self) -> None:
        super().setUp()
        self.test_solution = SolutionFactory.create()
        self.test_offer.solution = self.test_solution
        self.test_offer.save()
        self.client.login(username=self.user.username, password="secret")
        self.url = reverse(TestSolutionDeleteView.url_name, kwargs={"pk": self.test_solution.id})

    def tearDown(self) -> None:
        Solution.objects.all().delete()
        super().tearDown()

    @classmethod
    def tearDownClass(cls):
        """
        Clean up method after each test case.
        """
        Offer.objects.all().delete()
        Task.objects.all().delete()
        super().tearDownClass()

    def test_should_return_confirmation_page_on_get(self):
        """
        Test case to check if Solution Delete View returns confirmation page
        """
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "tasksapp/solution_confirm_delete.html")
        self.assertIn("object", response.context)

    def test_should_delete_not_accepted_solution(self):
        """
        Test case to check if not accepted solution is deleted
        """

        self.test_solution.accepted = False
        self.test_solution.save()
        response = self.client.post(self.url)

        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse("task-contractor-detail", kwargs={"pk": self.test_task.pk}))
        self.assertFalse(Solution.objects.filter(id=self.test_solution.id).exists())

    def test_should_not_delete_accepted_solution(self):
        """
        Test case to check if accepted solution is not deleted
        """

        self.test_solution.accepted = True
        self.test_solution.save()
        response = self.client.post(self.url)

        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse("task-contractor-detail", kwargs={"pk": self.test_task.pk}))
        self.assertTrue(Solution.objects.filter(id=self.test_solution.id).exists())

    def test_should_redirect_when_no_user_is_log_in(self):
        """
        Test whether the view correctly redirects to the login page when a non-logged-in user attempts to access it.
        """
        self.client.logout()
        response = self.client.get(self.url)
        self.assertRedirects(response, f"/users/accounts/login/?next={self.url}")

    def test_should_redirect_if_user_is_not_contractor(self):
        """
        Test if the client will be redirected if the current user is not contractor of the solution. Client will be
        redirected to detail view and another user to the dashboard.
        """
        self.client.login(username=self.client_user.username, password="secret")
        response = self.client.get(self.url)
        self.assertRedirects(response, reverse("task-detail", kwargs={"pk": self.test_task.pk}))

        another_user = UserFactory.create()
        self.client.login(username=another_user.username, password="secret")
        response = self.client.get(self.url, follow=True)
        self.assertRedirects(response, reverse("dashboard"))

    def test_should_handle_attempt_to_delete_nonexistent_solution(self):
        """
        Test case to check if attempting to delete a non-existent solution is handled correctly
        """
        temp_solution = SolutionFactory.create()
        temp_solution_id = temp_solution.id
        temp_solution.delete()
        response = self.client.post(reverse(TestSolutionDeleteView.url_name, kwargs={"pk": temp_solution_id}))
        self.assertEqual(response.status_code, 404)
