from django.urls import reverse
from factories.factories import OfferFactory, TaskFactory, UserFactory
from selenium.webdriver.common.by import By
from tasksapp.models import Offer

from .authenticated import AuthenticatedTestCase


class TestCreateOffer(AuthenticatedTestCase):
    """
    End to end browser test of creating new offer by the contractor
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


class TestEditOffer(AuthenticatedTestCase):
    """
    End to end browser test of editing existing offer by the contractor
    """

    url_name = "offer-edit"
    redirect_url = "offer-detail"

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.test_client = UserFactory.create()
        cls.test_task1 = TaskFactory.create(client=cls.test_client)
        cls.test_offer1 = OfferFactory.create(task=cls.test_task1, contractor=cls.user)
        cls.base_url = cls.live_server_url
        cls.url = cls.base_url + reverse(cls.url_name, args=[cls.test_offer1.id])
        cls.data = {
            "description": "New description",
            "days_to_complete": 3,
            "budget": 1100.00,
        }

    def tearDown(self) -> None:
        Offer.objects.all().delete()
        super().tearDown()

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()

    def test_should_edit_offer(self):
        navbar_tasks = self.driver.find_element(By.ID, "navbar-solve-tasks")
        navbar_tasks.click()
        navbar_tasks = self.driver.find_element(By.ID, "navbar-my-offers")
        navbar_tasks.click()
        navbar_find_task = self.driver.find_element(By.ID, "offer-detail")
        navbar_find_task.click()
        navbar_edit_offer = self.driver.find_element(By.ID, "offer-edit")
        navbar_edit_offer.click()
        self.assertIn(self.base_url + reverse(self.url_name, args=[self.test_offer1.id]), self.driver.current_url)
        description = self.driver.find_element(By.ID, "id_description")
        days_to_complete = self.driver.find_element(By.ID, "id_days_to_complete")
        budget = self.driver.find_element(By.ID, "id_budget")
        description.clear()
        description.send_keys(self.data.get("description"))
        days_to_complete.clear()
        days_to_complete.send_keys(self.data.get("days_to_complete"))
        budget.clear()
        budget.send_keys(self.data.get("budget"))
        submit = self.driver.find_element(By.CSS_SELECTOR, "button[type='submit']")
        submit.click()
        self.assertEqual(Offer.objects.filter(description=self.data["description"]).count(), 1)
        self.assertIn(self.base_url + reverse(self.redirect_url, args=[self.test_offer1.id]), self.driver.current_url)
