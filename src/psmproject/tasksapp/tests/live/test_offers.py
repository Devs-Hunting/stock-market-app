from django.urls import reverse
from factories.factories import TaskFactory, UserFactory
from selenium.webdriver.common.by import By
from tasksapp.models import Offer

from .authenticated import AuthenticatedTestCase


class TestCreateOffer(AuthenticatedTestCase):
    """
    End to end browser test of creating new offer by the client
    """

    url_name = "offer-create"
    redirect_url = "tasks-client-list"

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.test_client = UserFactory.create()
        cls.test_task1 = TaskFactory.create(client=cls.test_client)
        cls.base_url = cls.live_server_url
        cls.url = cls.base_url + reverse(cls.url_name, args=[cls.test_task1.id])
        cls.data = {
            "description": "Offer description",
            "days_to_complete": 12,
            "budget": 1220.50,
        }

    def tearDown(self) -> None:
        Offer.objects.all().delete()
        super().tearDown()

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()

    def test_should_create_offer(self):
        navbar_tasks = self.driver.find_element(By.ID, "navbar-solve-tasks")
        navbar_tasks.click()
        navbar_find_task = self.driver.find_element(By.ID, "navbar-find-task")
        navbar_find_task.click()
        navbar_create_offer = self.driver.find_element(By.LINK_TEXT, "create offer")
        navbar_create_offer.click()
        self.assertIn(self.base_url + reverse(self.url_name, args=[self.test_task1.id]), self.driver.current_url)
        description = self.driver.find_element(By.ID, "id_description")
        days_to_complete = self.driver.find_element(By.ID, "id_days_to_complete")
        budget = self.driver.find_element(By.ID, "id_budget")
        description.send_keys(self.data.get("description"))
        days_to_complete.send_keys(self.data.get("days_to_complete"))
        budget.send_keys(self.data.get("budget"))
        submit = self.driver.find_element(By.CSS_SELECTOR, "button[type='submit']")
        submit.click()
        self.assertEqual(Offer.objects.filter(description=self.data["description"]).count(), 1)
        self.assertIn(self.base_url + reverse(self.redirect_url), self.driver.current_url)
