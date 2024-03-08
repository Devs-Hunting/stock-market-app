import pytest  # noqa
from selenium.webdriver.common.by import By

from .settings import TEST_HOST


@pytest.mark.usefixtures("authenticated_test", "selenium_test")
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

    assert redirect_url in driver.current_url
