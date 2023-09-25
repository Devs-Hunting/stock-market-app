from datetime import datetime

from django.forms.models import model_to_dict
from django.test import Client, TestCase, TransactionTestCase
from django.urls import reverse
from factories.factories import OfferFactory, TaskFactory, UserFactory
from offerapp.models import Offer
from offerapp.views.contractor import SKILL_PREFIX
from tasksapp.models import Task
from usersapp.models import Skill

client = Client()


class TestContractorOfferListView(TransactionTestCase):
    """
    Test case for the contractor offer list view.
    """

    url_name = "offers-list"

    def setUp(self) -> None:
        """
        Set up method that is run before every individual test. Here it prepares test user and offers,
        logs in a user, and sets up a standard response object for use in the tests.
        """
        self.user = UserFactory.create()
        self.client_user = UserFactory.create()
        self.test_task1 = TaskFactory.create(client=self.client_user, title="UniqueTitle1")
        self.test_task2 = TaskFactory.create(client=self.client_user, title="UniqueTitle2")
        self.test_offer1 = OfferFactory.create(contractor=self.user, task=self.test_task1)
        self.test_offer2 = OfferFactory.create(contractor=self.user, task=self.test_task2)

        self.client.login(username=self.user.username, password="secret")
        self.response = self.client.get(reverse(TestContractorOfferListView.url_name))
        super().setUp()

    def tearDown(self):
        """
        Clean up method after each test case.
        """
        Task.objects.all().delete()
        Offer.objects.all().delete()

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
        self.assertTemplateUsed(self.response, "offerapp/offers_list.html")

    def test_should_return_correct_objects_when_request_is_sent(self):
        """
        Test whether the correct objects are returned when a request is sent to the view.
        """
        self.assertEqual(self.response.status_code, 200)
        self.assertTemplateUsed(self.response, "offerapp/offers_list.html")
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

        response = self.client.get(reverse(TestContractorOfferListView.url_name))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'href="?page=2"')
        self.assertEqual(len(response.context["object_list"]), 10)

    def test_should_redirect_if_not_logged_in(self):
        """
        Test whether the view correctly redirects to the login page if a not-logged-in user attempts to access it.
        """
        self.client.logout()
        self.response = self.client.get(reverse(TestContractorOfferListView.url_name))
        self.assertRedirects(self.response, "/users/accounts/login/?next=/offers/")

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
    template = "offerapp/task_search.html"

    @classmethod
    def setUpClass(cls) -> None:
        super().setUpClass()
        skills = ["python", "django", "java script", "flask"]
        cls.skills = []
        for skill in skills:
            cls.skills.append(Skill.objects.create(skill=skill))

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
        self.response = self.client.get(reverse(TestContractorTaskSearchView.url_name))

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
            temp_task = TaskFactory.create(client=self.client_user)

        response = self.client.get(reverse(TestContractorTaskSearchView.url_name))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'href="?page=2"')
        self.assertEqual(len(response.context["object_list"]), 10)

    def test_should_redirect_if_not_logged_in(self):
        """
        Test whether the view correctly redirects to the login page if a not-logged-in user attempts to access it.
        """
        self.client.logout()
        self.response = self.client.get(reverse(TestContractorTaskSearchView.url_name))
        self.assertRedirects(self.response, "/users/accounts/login/?next=/offers/task-search")

    def test_elements_should_be_sorted_by_id_from_newest(self):
        """
        Test whether the returned tasks are sorted by id from newest.
        """
        self.assertEqual(list(self.response.context["object_list"])[0], self.test_task3)

    def test_should_return_all_context_information_on_get(self):
        skills = self.response.context.get("skills")
        self.assertIsNotNone(skills)
        self.assertListEqual(skills, [model_to_dict(skill) for skill in self.skills])
        form = self.response.context.get("form")
        self.assertIsNotNone(form)
        skill_prefix = self.response.context.get("skill_id_prefix")
        self.assertIsNotNone(skill_prefix)

    def test_should_return_objects_filtered_by_title_when_query_posted(self):
        response = self.client.post(
            reverse(self.url_name),
            {
                "query": self.test_task1.title,
            },
        )
        self.assertQuerysetEqual(response.context["object_list"], [self.test_task1])

    def test_should_return_objects_filtered_by_description_when_query_posted(self):
        response = self.client.post(
            reverse(self.url_name),
            {
                "query": self.test_task1.description[:10],
            },
        )
        self.assertQuerysetEqual(response.context["object_list"], [self.test_task1])

    def test_should_return_objects_filtered_by_budget_on_post(self):
        """
        Test if response contains only tasks with minimum budget higher/equal than posted in filter
        """
        response = self.client.post(
            reverse(self.url_name),
            {
                "budget": self.test_task2.budget,
            },
        )
        self.assertQuerysetEqual(response.context["object_list"], [self.test_task3, self.test_task2])

    def test_should_return_objects_filtered_by_date_on_post(self):
        """
        Test if response contains only tasks with realization date later or same as posted in filter
        """

        response = self.client.post(
            reverse(self.url_name),
            {
                "realization_time": self.test_task2.realization_time,
            },
        )
        self.assertQuerysetEqual(response.context["object_list"], [self.test_task2, self.test_task1])

    def test_should_return_objects_filtered_by_skills_on_post(self):
        """
        Test if response contains only tasks that have all skills listed in post
        """

        response = self.client.post(
            reverse(self.url_name),
            {
                f"{SKILL_PREFIX}1": self.skills[0].skill,
                f"{SKILL_PREFIX}2": self.skills[1].skill,
            },
        )
        self.assertQuerysetEqual(response.context["object_list"], [self.test_task1])

    def test_should_return_skill_list_without_selected_on_post(self):

        response = self.client.post(
            reverse(self.url_name),
            {
                f"{SKILL_PREFIX}1": self.skills[0].skill,
                f"{SKILL_PREFIX}2": self.skills[1].skill,
            },
        )

        skills = response.context.get("skills")
        self.assertIsNotNone(skills)
        self.assertListEqual(skills, [model_to_dict(skill) for skill in self.skills[2:]])


class TestContractorOfferCreateView(TestCase):
    """
    Test case for the contractor's create view.
    """

    url_name = "offer-create"
    template = "offerapp/offer_form.html"

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
        self.data = {
            "description": "New offer 7620192",
            "realization_time": "2023-12-31",
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
        self.assertRedirects(response, f"/users/accounts/login/?next=/offers/add/task/{self.test_task1.id}")


class TestContractorOfferEditView(TestCase):
    """
    Test case for the contractor's edit view.
    """

    url_name = "offer-edit"
    template = "offerapp/offer_form.html"

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
        self.client_user = UserFactory.create()
        self.test_task = TaskFactory.create(client=self.client_user)
        self.test_offer = OfferFactory.create(contractor=self.user, task=self.test_task)

        self.client.login(username=self.user.username, password="secret")
        self.url = reverse(TestContractorOfferEditView.url_name, kwargs={"pk": self.test_offer.id})

        self.data = {
            "description": "New offer 7620192",
            "realization_time": "2023-12-31",
            "budget": 1220.12,
        }

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
        response = self.client.post(self.url, data=self.data, follow=True)

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
        self.assertRedirects(response, f"/users/accounts/login/?next=/offers/{self.test_offer.id}/edit")

    def test_should_redirect_if_user_is_not_contractor(self):
        """
        Test if the client will be redirected if the current user is not contractor of the offer.
        """

        another_user = UserFactory.create()
        self.client.login(username=another_user.username, password="secret")
        response = self.client.get(self.url)
        self.assertRedirects(response, reverse("offer-detail", kwargs={"pk": self.test_offer.pk}))
