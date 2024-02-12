from django.urls import reverse
from selenium.webdriver.common.by import By
from tasksapp.models import Task

from .authenticated import AuthenticatedTestCase


class TestCreateTask(AuthenticatedTestCase):
    """
    End to end browser test of creating new task by the client
    """

    url_name = "task-create"
    redirect_url = "tasks-client-list"

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.base_url = cls.live_server_url
        cls.url = cls.base_url + reverse(cls.url_name)
        cls.data = {
            "title": "Task Title",
            "description": "Task descrption",
            "days_to_complete": 31,
            "budget": 1220.12,
        }

    def tearDown(self) -> None:
        Task.objects.all().delete()
        super().tearDown()

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()

    def test_should_create_task(self):
        navbar_tasks = self.driver.find_element(By.ID, "navbar-tasks")
        navbar_tasks.click()
        navbar_create_task = self.driver.find_element(By.ID, "navbar-create-task")
        navbar_create_task.click()
        self.assertIn(self.base_url + reverse(self.url_name), self.driver.current_url)
        title = self.driver.find_element(By.ID, "id_title")
        description = self.driver.find_element(By.ID, "id_description")
        days_to_complete = self.driver.find_element(By.ID, "id_days_to_complete")
        budget = self.driver.find_element(By.ID, "id_budget")
        title.send_keys(self.data.get("title"))
        description.send_keys(self.data.get("description"))
        days_to_complete.send_keys(self.data.get("days_to_complete"))
        budget.send_keys(self.data.get("budget"))
        submit = self.driver.find_element(By.CSS_SELECTOR, "button[type='submit']")
        submit.click()
        self.assertEqual(Task.objects.filter(title=self.data["title"]).count(), 1)
        self.assertIn(self.base_url + reverse(self.redirect_url), self.driver.current_url)
