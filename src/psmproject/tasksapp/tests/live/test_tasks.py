from django.urls import reverse
from factories.factories import TaskFactory
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


class TestTaskList(AuthenticatedTestCase):
    """
    End to end browser test of displaying list of tasks by the clien
    """

    url_name = "tasks-client-list"

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.base_url = cls.live_server_url
        cls.url = cls.base_url + reverse(cls.url_name)
        cls.test_task1 = TaskFactory.create(client=cls.user)
        cls.test_task2 = TaskFactory.create(client=cls.user)
        cls.tasks = [cls.test_task2, cls.test_task1]

    def test_should_display_tasks_list(self):
        navbar_tasks = self.driver.find_element(By.ID, "navbar-tasks")
        navbar_tasks.click()
        navbar_create_task = self.driver.find_element(By.ID, "navbar-tasks-list")
        navbar_create_task.click()
        self.assertIn(self.url, self.driver.current_url)
        tasks_list = self.driver.find_element(By.XPATH, "/ html / body / div[2] / div / div / ul")
        items = tasks_list.find_elements(By.TAG_NAME, "li")
        self.assertEqual(len(items), len(self.tasks))
        index = 0
        for item in items:
            link = item.find_elements(By.XPATH, "./ span / a")[0]
            href = "/" + "/".join(link.get_attribute("href").split("/")[-2:])
            self.assertEqual(href, f"/tasks/{self.tasks[index].id}")
            title_span = link.find_elements(By.TAG_NAME, "span")[0]
            self.assertEqual(title_span.text, self.tasks[index].title)
            index += 1


class TestDisplayTaskDetails(AuthenticatedTestCase):
    """
    End to end browser test of displaying details of one task
    """

    url_name = "task-detail"

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.base_url = cls.live_server_url

        cls.test_task1 = TaskFactory.create(client=cls.user)
        cls.test_task2 = TaskFactory.create(client=cls.user)
        cls.url = cls.base_url + reverse(cls.url_name, kwargs={"pk": cls.test_task2.pk})
        cls.tasks = [cls.test_task2, cls.test_task1]

    def test_should_display_task_details(self):
        navbar_tasks = self.driver.find_element(By.ID, "navbar-tasks")
        navbar_tasks.click()
        navbar_create_task = self.driver.find_element(By.ID, "navbar-tasks-list")
        navbar_create_task.click()
        tasks_list = self.driver.find_element(By.XPATH, "/ html / body / div[2] / div / div / ul")
        first_task = tasks_list.find_elements(By.TAG_NAME, "li")[0]
        link = first_task.find_elements(By.XPATH, "./ span / a")[0]
        link.click()
        self.assertIn(self.url, self.driver.current_url)
