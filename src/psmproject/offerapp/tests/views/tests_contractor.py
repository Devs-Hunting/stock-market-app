from django.forms.models import model_to_dict
from django.test import Client, TestCase, TransactionTestCase
from django.urls import reverse
from factories.factories import OfferFactory, TaskFactory, UserFactory
from offerapp.models import Offer
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
        skills = ["python", "django", "java script", "flask"]
        cls.skills = []
        for skill in skills:
            cls.skills.append(Skill.objects.create(skill=skill))
        super().setUpClass()

    def setUp(self) -> None:
        """
        Set up method that is run before every individual test. Here it prepares test user and tasks,
        logs in a user, and sets up a standard response object for use in the tests. Tasks 1-3 should be returned.
        Task 4 is a task for which an offer was made. Task 5 is a task created by current user. Tasks 1-3 are ordered
        by budget the smallest first. Tasks 1-3 are ordered by realization time, the latest first.
        """
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
