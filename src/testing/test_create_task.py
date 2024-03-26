import pytest  # noqa
from selenium.webdriver.common.by import By

from .settings import TEST_HOST

pytest_plugins = [
    "testing.fixtures.authenticated",
]


def test_should_create_task(authenticated_test):
    driver, test_user = authenticated_test
    url = TEST_HOST + "/tasks/add/"
    redirect_url = TEST_HOST + "/tasks/"

    data = {
        "title": "Task Title",
        "description": "Task descrption",
        "days_to_complete": 31,
        "budget": 1220.12,
    }

    # navigate
    navbar_tasks = driver.find_element(By.ID, "navbar-tasks")
    navbar_tasks.click()
    navbar_create_task = driver.find_element(By.ID, "navbar-create-task")
    navbar_create_task.click()

    assert url in driver.current_url

    # fill form and submit
    title = driver.find_element(By.ID, "id_title")
    description = driver.find_element(By.ID, "id_description")
    days_to_complete = driver.find_element(By.ID, "id_days_to_complete")
    budget = driver.find_element(By.ID, "id_budget")
    title.send_keys(data.get("title"))
    description.send_keys(data.get("description"))
    days_to_complete.send_keys(data.get("days_to_complete"))
    budget.send_keys(data.get("budget"))
    submit = driver.find_element(By.CSS_SELECTOR, "button[type='submit']")
    submit.click()

    # redirected to tasks list
    assert redirect_url in driver.current_url

    # check if new task is first on the list
    tasks_list = driver.find_element(By.ID, "tasks-list")
    tasks = tasks_list.find_elements(By.TAG_NAME, "li")
    new_task_title = tasks[0].find_element(By.XPATH, ".//a[1]//div//strong").text
    assert new_task_title == data["title"]
